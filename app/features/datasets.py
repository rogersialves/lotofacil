"""Construção dos datasets utilizados pelos modelos de IA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import pandas as pd

from app.etl import ConcursoFiltro, carregar_concursos

MOLDURA = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}


@dataclass
class DatasetConfig:
    freq_janelas: Tuple[int, ...] = (10, 20, 50)
    presenca_janelas: Tuple[int, ...] = (5, 10, 20)


def _carregar_pivot(atualizar: bool = False) -> pd.DataFrame:
    filtro = ConcursoFiltro(atualizar=atualizar, formato="long")
    long_df = carregar_concursos(filtro).sort_values("Concurso")
    long_df["Sorteada"] = 1
    pivot = (
        long_df.pivot_table(
            index="Concurso",
            columns="Dezena",
            values="Sorteada",
            aggfunc="max",
            fill_value=0,
        )
        .sort_index()
        .astype(int)
    )

    for dezena in range(1, 26):
        if dezena not in pivot.columns:
            pivot[dezena] = 0

    pivot = pivot.reindex(sorted(pivot.columns), axis=1)
    return pivot


def preparar_dataset_dezena(
    atualizar: bool = False,
    config: DatasetConfig = DatasetConfig(),
) -> pd.DataFrame:
    """
    Retorna DataFrame no formato (concurso, dezena, features, sorteada).
    """

    pivot = _carregar_pivot(atualizar=atualizar)
    history = pivot.shift(1).fillna(0)

    freq_frames = {
        janela: history.rolling(window=janela, min_periods=1).sum()
        for janela in config.freq_janelas
    }
    atraso_df = _calcular_atraso_dataframe(history)

    registros = []
    for concurso in pivot.index[1:]:
        for dezena in pivot.columns:
            linha = {
                "concurso": int(concurso),
                "dezena": int(dezena),
                "sorteada": int(pivot.at[concurso, dezena]),
                "atraso": int(atraso_df.at[concurso, dezena]),
            }

            for janela, freq_df in freq_frames.items():
                freq_val = int(freq_df.at[concurso, dezena])
                linha[f"freq_{janela}"] = freq_val
                linha[f"presenca_{janela}"] = 1 if freq_val > 0 else 0

            registros.append(linha)

    return pd.DataFrame(registros)


def _calcular_atraso_dataframe(history: pd.DataFrame) -> pd.DataFrame:
    atraso = pd.DataFrame(index=history.index, columns=history.columns, dtype=int)
    contadores: Dict[int, int] = {dezena: 0 for dezena in history.columns}

    for concurso in history.index:
        for dezena in history.columns:
            if history.at[concurso, dezena] == 1:
                contadores[dezena] = 0
            else:
                contadores[dezena] += 1
            atraso.at[concurso, dezena] = contadores[dezena]
    return atraso


def preparar_dataset_jogo(atualizar: bool = False) -> pd.DataFrame:
    """
    Cria dataset por concurso (15 dezenas) com vetores 25 bits e agregados.
    """

    pivot = _carregar_pivot(atualizar=atualizar)
    dataset = pivot.copy()
    dataset.columns = [f"dezena_{int(col):02d}" for col in dataset.columns]

    pares_cols = [col for col in dataset.columns if int(col.split("_")[1]) % 2 == 0]
    moldura_cols = [col for col in dataset.columns if int(col.split("_")[1]) in MOLDURA]

    dataset["pares"] = dataset[pares_cols].sum(axis=1)
    dataset["impares"] = 15 - dataset["pares"]
    dataset["moldura"] = dataset[moldura_cols].sum(axis=1)
    dataset["miolo"] = 15 - dataset["moldura"]
    dataset["soma_dezenas"] = _calcular_soma_dezenas(pivot)

    dataset["score_real"] = 1
    dataset.reset_index(inplace=True)
    dataset.rename(columns={"Concurso": "concurso"}, inplace=True)
    return dataset


def _calcular_soma_dezenas(pivot: pd.DataFrame) -> pd.Series:
    soma = pd.Series(0, index=pivot.index, dtype=int)
    for dezena in pivot.columns:
        soma += pivot[dezena] * int(dezena)
    return soma
