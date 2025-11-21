"""Serviços de IA: sugestão de dezenas e scoring com modelo real."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence

import joblib
import numpy as np

from app.features import DatasetConfig, calcular_estatisticas_avancadas, preparar_dataset_dezena
from app.ml.pipelines.dezena import carregar_modelo_dezena
from app.core.logging import log_entretenimento


def sugerir_dezenas(
    n_dezenas: int,
    modo: str = "mix",
    atualizar: bool = False,
    usar_modelo: bool = True,
) -> Dict[str, object]:
    """
    Seleciona dezenas com base no modelo treinado ou heurísticas.
    """

    if not 15 <= n_dezenas <= 21:
        raise ValueError("n_dezenas deve estar entre 15 e 21.")

    stats = calcular_estatisticas_avancadas(atualizar=atualizar)["dezenas"]

    if usar_modelo:
        try:
            modelo = carregar_modelo_dezena()
            dataset = preparar_dataset_dezena(atualizar=atualizar, config=DatasetConfig())
            ultimos = (
                dataset.groupby("dezena").tail(1).set_index("dezena").drop(columns=["sorteada"])
            )
            probabilidades = modelo.predict_proba(ultimos)[:, 1]
            ranking = sorted(
                zip(ultimos.index.tolist(), probabilidades),
                key=lambda item: item[1],
                reverse=True,
            )
            selecionadas = [dezena for dezena, _ in ranking[:n_dezenas]]
        except FileNotFoundError:
            selecionadas = _selecionar_heuristica(stats, n_dezenas, modo)
            usar_modelo = False
    else:
        selecionadas = _selecionar_heuristica(stats, n_dezenas, modo)

    selecionadas.sort()

    log_entretenimento("Sugestão de dezenas")
    return {
        "modo": "modelo" if usar_modelo else modo,
        "n_dezenas": n_dezenas,
        "dezenas": selecionadas,
        "disclaimer": "Sugestão baseada em dados históricos; uso recreativo.",
    }


def _selecionar_heuristica(stats: Dict[int, Dict[str, float]], n_dezenas: int, modo: str) -> List[int]:
    def score(item: Dict[str, float]) -> float:
        freq = item.get("freq_50", 0)
        atraso = item.get("atraso_atual", 0)
        presenca = item.get("presenca_10", 0)
        if modo == "probabilidade":
            return freq + presenca
        if modo == "atraso":
            return atraso
        return freq * 0.6 + atraso * 0.3 + presenca * 0.1

    ordenado = sorted(stats.items(), key=lambda kv: score(kv[1]), reverse=True)
    return [dezena for dezena, _ in ordenado[:n_dezenas]]


def score_jogos(
    jogos: Sequence[Sequence[int]],
    atualizar: bool = False,
) -> List[Dict[str, object]]:
    """
    Atribui score via modelo de jogo treinado (fallback para heurística).
    """

    try:
        modelo = joblib.load(Path("./models/jogo/model.joblib"))
        # Prepara estrutura 25 bits
        representacoes = []
        for jogo in jogos:
            if len(jogo) != 15:
                raise ValueError("Cada jogo deve conter exatamente 15 dezenas.")
            vetor = [1 if (i + 1) in jogo else 0 for i in range(25)]
            representacoes.append(vetor)

        proba = modelo.predict_proba(np.array(representacoes))[:, 1]
        resultados = [
            {"jogo": sorted(jogo), "score": round(float(score), 4)}
            for jogo, score in zip(jogos, proba)
        ]
        return resultados
    except FileNotFoundError:
        stats = calcular_estatisticas_avancadas(atualizar=atualizar)["dezenas"]
        resultados: List[Dict[str, object]] = []
        for jogo in jogos:
            if len(jogo) != 15:
                raise ValueError("Cada jogo deve conter exatamente 15 dezenas.")
            score_total = 0.0
            for dezena in jogo:
                info = stats.get(dezena, {})
                score_total += info.get("freq_50", 0) * 0.5
                score_total += info.get("presenca_10", 0) * 0.3
                score_total += info.get("atraso_atual", 0) * 0.2
            resultados.append(
                {
                    "jogo": sorted(jogo),
                    "score": round(score_total / len(jogo), 4),
                }
            )
        log_entretenimento("Score de jogos (heurístico)")
        return resultados
