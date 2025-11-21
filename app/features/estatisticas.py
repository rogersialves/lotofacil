"""Cálculo de estatísticas avançadas usadas na IA e dashboards."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Tuple

import pandas as pd

from app.etl import ConcursoFiltro, carregar_concursos

MOLDURA = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
MIOLO = set(range(1, 26)) - MOLDURA


def _carregar_long(atualizar: bool = False) -> pd.DataFrame:
    filtro = ConcursoFiltro(atualizar=atualizar, formato="long")
    df = carregar_concursos(filtro)
    return df.sort_values("Concurso")


def calcular_estatisticas_avancadas(
    atualizar: bool = False,
    janelas_freq: Tuple[int, ...] = (10, 20, 50),
    janelas_presenca: Tuple[int, ...] = (5, 10, 20),
) -> Dict[str, object]:
    """
    Gera estatísticas por dezena e distribuições globais.
    """

    df = _carregar_long(atualizar=atualizar)
    dezenas_metrics = _metricas_por_dezena(df, janelas_freq, janelas_presenca)
    distribuicoes = _distribuicoes_jogos(df)
    return {"dezenas": dezenas_metrics, "distribuicoes": distribuicoes}


def _metricas_por_dezena(
    df: pd.DataFrame,
    janelas_freq: Iterable[int],
    janelas_presenca: Iterable[int],
) -> Dict[int, Dict[str, float]]:
    ultimo = int(df["Concurso"].max())
    primeiro = int(df["Concurso"].min())
    base = {dezena: {} for dezena in range(1, 26)}

    for janela in janelas_freq:
        limite = max(primeiro, ultimo - janela + 1)
        subset = df[df["Concurso"] >= limite]
        contagem = subset["Dezena"].value_counts()
        for dezena in base:
            base[dezena][f"freq_{janela}"] = int(contagem.get(dezena, 0))

    atrasos = _calcular_atrasos(df, ultimo)
    for dezena, atraso in atrasos.items():
        base[dezena]["atraso_atual"] = atraso

    for janela in janelas_presenca:
        limite = max(primeiro, ultimo - janela + 1)
        subset = df[df["Concurso"] >= limite]
        contagem = subset["Dezena"].value_counts()
        for dezena in base:
            base[dezena][f"presenca_{janela}"] = int(contagem.get(dezena, 0))

    return base


def _calcular_atrasos(df: pd.DataFrame, ultimo: int) -> Dict[int, int]:
    atrasos: Dict[int, int] = {}
    for dezena in range(1, 26):
        concursos = df[df["Dezena"] == dezena]["Concurso"]
        if concursos.empty:
            atrasos[dezena] = ultimo
        else:
            atrasos[dezena] = int(ultimo - concursos.max())
    return atrasos


def _distribuicoes_jogos(df: pd.DataFrame) -> Dict[str, List[Dict[str, float]]]:
    jogos = df.groupby("Concurso")["Dezena"].apply(list)
    pares_impares = Counter()
    moldura_miolo = Counter()

    for dezenas in jogos:
        pares = sum(1 for dezena in dezenas if dezena % 2 == 0)
        impares = len(dezenas) - pares
        pares_impares[(pares, impares)] += 1

        moldura = sum(1 for dezena in dezenas if dezena in MOLDURA)
        miolo = len(dezenas) - moldura
        moldura_miolo[(moldura, miolo)] += 1

    total = len(jogos)
    return {
        "pares_impares": _formata_distribuicao(pares_impares, total, ("pares", "impares")),
        "moldura_miolo": _formata_distribuicao(moldura_miolo, total, ("moldura", "miolo")),
    }


def _formata_distribuicao(
    contagens: Counter,
    total: int,
    chaves: Tuple[str, str],
) -> List[Dict[str, float]]:
    distribuicao: List[Dict[str, float]] = []
    for (valor_a, valor_b), ocorrencias in sorted(contagens.items(), reverse=True):
        percentual = (ocorrencias / total) * 100 if total else 0
        distribuicao.append(
            {
                chaves[0]: valor_a,
                chaves[1]: valor_b,
                "ocorrencias": ocorrencias,
                "percentual": round(percentual, 2),
            }
        )
    return distribuicao
