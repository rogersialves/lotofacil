"""Geração do dataset de estratégias de fechamento."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List

import pandas as pd

from app.fechamentos import listar_modelos
from app.features.datasets import preparar_dataset_jogo
from app.fechamentos import aplicar_fechamento
from app.ia.services import score_jogos

VALOR_APOSTA = 3.0
DESTINO_DATASET = Path("./base/dataset_estrategias.csv")
GARANTIA_PESO = {
    "15": 1.0,
    "14": 0.85,
    "13": 0.7,
    "variada": 0.6,
}


def gerar_dataset_estrategias(atualizar: bool = False) -> pd.DataFrame:
    """
    Cria um dataset sintético com métricas para cada modelo de fechamento.
    """

    base_jogos = preparar_dataset_jogo(atualizar=atualizar)
    stats_globais = base_jogos[["pares", "moldura", "soma_dezenas"]].describe()

    registros: List[Dict[str, float]] = []
    for modelo in listar_modelos():
        baseline_dezenas = list(range(1, modelo.n_dezenas + 1))
        jogos = aplicar_fechamento(baseline_dezenas, modelo.id_modelo)
        scores = score_jogos(jogos)
        score_medio = sum(item["score"] for item in scores) / len(scores)
        registro = _simular_modelo(modelo, stats_globais)
        registro["score_jogos_medio"] = round(score_medio, 4)
        registros.append(registro)

    dataset = pd.DataFrame(registros)
    salvar_dataset_estrategias(dataset)
    return dataset


def _simular_modelo(modelo, stats_globais: pd.DataFrame) -> Dict[str, float]:
    combinacoes_total = math.comb(modelo.n_dezenas, 15)
    cobertura_teorica = modelo.n_jogos / combinacoes_total
    densidade_dezenas = modelo.n_dezenas / 25
    preco_total = modelo.n_jogos * VALOR_APOSTA
    peso_garantia = GARANTIA_PESO.get(modelo.tipo_garantia, 0.6)

    score_base = (cobertura_teorica * 0.6 + densidade_dezenas * 0.4) * peso_garantia
    esperado_14 = round(score_base * 10, 4)
    esperado_13 = round(score_base * 30, 4)
    roi_estimado = round((esperado_13 * 30 + esperado_14 * 120) / max(preco_total, 1), 4)

    return {
        "id_modelo": modelo.id_modelo,
        "n_dezenas": modelo.n_dezenas,
        "n_jogos": modelo.n_jogos,
        "tipo_garantia": modelo.tipo_garantia,
        "precisa_acertar": modelo.precisa_acertar,
        "preco_total": preco_total,
        "cobertura_teorica": round(cobertura_teorica, 6),
        "densidade_dezenas": round(densidade_dezenas, 4),
        "score_base": round(score_base, 5),
        "esperado_14": esperado_14,
        "esperado_13": esperado_13,
        "roi_estimado": roi_estimado,
        "media_pares_historico": float(stats_globais.loc["mean", "pares"]),
        "media_moldura_historico": float(stats_globais.loc["mean", "moldura"]),
        "soma_dezenas_media": float(stats_globais.loc["mean", "soma_dezenas"]),
    }


def salvar_dataset_estrategias(dataset: pd.DataFrame, destino: Path = DESTINO_DATASET) -> Path:
    """Persiste o dataset de estratégias para uso em treinamento."""

    destino.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(destino, index=False)
    return destino
