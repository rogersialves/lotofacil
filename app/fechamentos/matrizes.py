"""Leitura e aplicação das matrizes de fechamento."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Sequence

from app.fechamentos.catalogo import ModeloFechamento, obter_modelo

MATRIZ_PATH = Path("./dados/fechamentos/matrizes.json")

with MATRIZ_PATH.open("r", encoding="utf8") as f:
    MATRIZES: Dict[str, List[List[int]]] = json.load(f)


def obter_matriz(id_modelo: str) -> List[List[int]]:
    """Retorna a matriz de um modelo específico."""

    if id_modelo not in MATRIZES:
        raise ValueError(f"Matriz para o modelo '{id_modelo}' não encontrada.")
    return MATRIZES[id_modelo]


def aplicar_fechamento(
    dezenas_usuario: Sequence[int],
    id_modelo: str,
) -> List[List[int]]:
    """
    Aplica a matriz de fechamento aos índices fornecidos pelo usuário.
    """

    modelo: ModeloFechamento = obter_modelo(id_modelo)
    if len(dezenas_usuario) != modelo.n_dezenas:
        raise ValueError(
            f"Modelo {id_modelo} requer {modelo.n_dezenas} dezenas, "
            f"mas foram fornecidas {len(dezenas_usuario)}."
        )

    dezenas_ordenadas = sorted(dezenas_usuario)
    jogos = []
    matriz = obter_matriz(id_modelo)

    for linha in matriz:
        jogo = [dezenas_ordenadas[idx - 1] for idx in linha]
        jogos.append(sorted(jogo))

    return jogos
