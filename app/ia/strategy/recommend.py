"""Heurística inicial para recomendação de n_dezenas + modelo."""

from __future__ import annotations

import pandas as pd

from app.features.estrategias import gerar_dataset_estrategias


def sugerir_estrategias(
    orçamento: float,
    perfil: str = "balanceado",
    atualizar: bool = False,
    limite: int = 5,
) -> pd.DataFrame:
    """
    Ranqueia estratégias dentro de um orçamento e perfil desejado.
    """

    dataset = gerar_dataset_estrategias(atualizar=atualizar)
    filtrado = dataset[dataset["preco_total"] <= orçamento].copy()

    if filtrado.empty:
        return pd.DataFrame()

    if perfil == "conservador":
        filtrado.loc[:, "ranking"] = filtrado["score_base"] * 0.6 + filtrado["roi_estimado"] * 0.4
    elif perfil == "agressivo":
        filtrado.loc[:, "ranking"] = filtrado["roi_estimado"] * 0.7 + filtrado["esperado_14"] * 0.3
    else:
        filtrado.loc[:, "ranking"] = (
            filtrado["score_base"] * 0.4
            + filtrado["roi_estimado"] * 0.4
            + filtrado["score_jogos_medio"] * 0.2
        )

    filtrado = filtrado.sort_values("ranking", ascending=False)
    return filtrado.head(limite)
