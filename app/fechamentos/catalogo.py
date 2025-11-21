"""Catálogo básico de modelos de fechamento suportados pelo sistema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ModeloFechamento:
    id_modelo: str
    descricao: str
    tipo_garantia: str
    n_dezenas: int
    precisa_acertar: int
    n_jogos: int
    indicador_premios_extras: bool = False

    @property
    def preco_total(self) -> float:
        valor_jogo = 3.0
        return round(self.n_jogos * valor_jogo, 2)


MODEL_CATALOG: List[ModeloFechamento] = [
    ModeloFechamento(
        id_modelo="F17-A",
        descricao="17 dezenas – garante 14 pontos acertando 15",
        tipo_garantia="14",
        n_dezenas=17,
        precisa_acertar=15,
        n_jogos=32,
    ),
    ModeloFechamento(
        id_modelo="F18-A",
        descricao="18 dezenas – garante 13 pontos acertando 15",
        tipo_garantia="13",
        n_dezenas=18,
        precisa_acertar=15,
        n_jogos=50,
    ),
    ModeloFechamento(
        id_modelo="F18-B",
        descricao="18 dezenas – foco em prêmios intermediários",
        tipo_garantia="variada",
        n_dezenas=18,
        precisa_acertar=14,
        n_jogos=26,
        indicador_premios_extras=True,
    ),
    ModeloFechamento(
        id_modelo="F19-A",
        descricao="19 dezenas – combina custo/benefício garantindo 13",
        tipo_garantia="13",
        n_dezenas=19,
        precisa_acertar=15,
        n_jogos=80,
    ),
    ModeloFechamento(
        id_modelo="F20-A",
        descricao="20 dezenas – aproximação premium com chance de 14",
        tipo_garantia="14",
        n_dezenas=20,
        precisa_acertar=15,
        n_jogos=120,
    ),
    ModeloFechamento(
        id_modelo="F21-A",
        descricao="21 dezenas – modelo agressivo buscando 14/15",
        tipo_garantia="variada",
        n_dezenas=21,
        precisa_acertar=15,
        n_jogos=210,
        indicador_premios_extras=True,
    ),
]


def listar_modelos() -> List[ModeloFechamento]:
    """Retorna cópia do catálogo cadastrado."""

    return list(MODEL_CATALOG)


def obter_modelo(id_modelo: str) -> ModeloFechamento:
    """Busca um modelo pelo identificador."""

    for modelo in MODEL_CATALOG:
        if modelo.id_modelo == id_modelo:
            return modelo
    raise ValueError(f"Modelo de fechamento '{id_modelo}' não encontrado.")
