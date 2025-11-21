"""Funções utilitárias para ingestão e leitura do histórico de concursos."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional

import pandas as pd

from dados import scrapping_resultados

RESULTADOS_CSV = scrapping_resultados.DESTINO_PADRAO
CONCURSOS_LONG_CSV = scrapping_resultados.DESTINO_LONG
ESTATISTICAS_JSON = scrapping_resultados.DESTINO_STATS


@dataclass
class ConcursoFiltro:
    limit: int = 100
    offset: int = 0
    formato: Literal["wide", "long"] = "wide"
    atualizar: bool = False


def carregar_concursos(
    filtro: ConcursoFiltro = ConcursoFiltro(),
) -> pd.DataFrame:
    """
    Carrega os concursos em formato largo (default) ou longo.
    """

    if filtro.atualizar or not RESULTADOS_CSV.exists():
        scrapping_resultados.atualizar_resultados()

    if filtro.formato == "long":
        if filtro.atualizar or not CONCURSOS_LONG_CSV.exists():
            # Garantir que a visão esteja atualizada
            base = pd.read_csv(RESULTADOS_CSV, sep=";", encoding="utf8")
            scrapping_resultados.gerar_concursos_long(base, CONCURSOS_LONG_CSV)
        df = pd.read_csv(CONCURSOS_LONG_CSV, sep=";", encoding="utf8")
    else:
        df = pd.read_csv(RESULTADOS_CSV, sep=";", encoding="utf8")

    return df


def listar_concursos(filtro: ConcursoFiltro = ConcursoFiltro()) -> List[Dict[str, object]]:
    """Retorna um subconjunto paginado dos concursos no formato amigável."""

    df = carregar_concursos(filtro)
    df = df.sort_values("Concurso")
    fatia = df.iloc[filtro.offset : filtro.offset + filtro.limit]
    registros: List[Dict[str, object]] = []

    for _, row in fatia.iterrows():
        registros.append(_normalizar_registro(row.to_dict()))
    return registros


def _normalizar_registro(registro: Dict[str, object]) -> Dict[str, object]:
    """Converte chaves do CSV para snake_case com nomes amigáveis."""

    mapeado = {}
    for key, value in registro.items():
        novo_nome = (
            key.lower()
            .replace(" ", "_")
            .replace("á", "a")
            .replace("ó", "o")
            .replace("ú", "u")
        )
        if novo_nome.startswith("b"):
            mapeado[novo_nome] = int(value)
        elif novo_nome == "concurso":
            mapeado["concurso"] = int(value)
        elif novo_nome == "ganhou":
            mapeado["ganhou"] = int(value)
        else:
            mapeado[novo_nome] = value
    return mapeado


def carregar_resumo(atualizar: bool = False) -> Optional[dict]:
    """
    Retorna informações básicas do último concurso disponível.
    """

    concursos = carregar_concursos(
        ConcursoFiltro(atualizar=atualizar, limit=1, offset=0, formato="wide")
    )
    if concursos.empty:
        return None
    return scrapping_resultados.obter_resumo_ultimo_concurso(concursos)


def carregar_estatisticas(atualizar: bool = False) -> Dict[str, object]:
    """
    Retorna as estatísticas básicas (frequência de dezenas, totais, etc.).
    """

    if atualizar or not ESTATISTICAS_JSON.exists():
        scrapping_resultados.atualizar_resultados()

    return json.loads(ESTATISTICAS_JSON.read_text(encoding="utf8"))
