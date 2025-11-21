"""Motor de simulação/backtest usando resultados históricos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Sequence

import pandas as pd

from app.auditoria.storage import ResultadoAposta, salvar_resultados
from app.core.logging import log_entretenimento
from app.etl import ConcursoFiltro, carregar_concursos


@dataclass
class ResultadoSimulacao:
    concurso: int
    acertos: int
    premio_estimado: float


PREMIOS_FIXOS = {11: 6.0, 12: 12.0, 13: 30.0}


def carregar_resultados(atualizar: bool = False) -> pd.DataFrame:
    """Carrega os concursos reais em formato wide."""

    filtro = ConcursoFiltro(atualizar=atualizar, formato="wide")
    return carregar_concursos(filtro)


def conferir_jogos(
    jogos: Sequence[Sequence[int]],
    concursos: pd.DataFrame,
) -> List[ResultadoSimulacao]:
    """Compara cada jogo com todos os concursos e contabiliza os acertos."""

    col_dezenas = [col for col in concursos.columns if col.startswith("B")]
    resultados: List[ResultadoSimulacao] = []

    for _, linha in concursos.iterrows():
        concurso_id = int(linha["Concurso"])
        sorteio = set(int(linha[col]) for col in col_dezenas)
        for jogo in jogos:
            acertos = len(sorteio.intersection(set(jogo)))
            if acertos >= 11:
                premio = PREMIOS_FIXOS.get(acertos, 0.0)
                resultados.append(
                    ResultadoSimulacao(
                        concurso=concurso_id,
                        acertos=acertos,
                        premio_estimado=premio,
                    )
                )
    return resultados


def simular_intervalo(
    jogos: Sequence[Sequence[int]],
    intervalo: slice,
    atualizar: bool = False,
    registrar: bool = False,
) -> Dict[str, object]:
    concursos = carregar_resultados(atualizar=atualizar).iloc[intervalo]
    return _montar_relatorio(jogos, concursos, registrar=registrar)


def simular_ultimos(
    jogos: Sequence[Sequence[int]],
    ultimos: int = 200,
    atualizar: bool = False,
    registrar: bool = False,
) -> Dict[str, object]:
    """
    Simula a estratégia considerando apenas os últimos N concursos.
    """

    if ultimos <= 0:
        raise ValueError("O parâmetro 'ultimos' deve ser positivo.")

    concursos = carregar_resultados(atualizar=atualizar)
    total = len(concursos)
    inicio = max(total - ultimos, 0)
    fatia = concursos.iloc[inicio:total]
    return _montar_relatorio(jogos, fatia, registrar=registrar)


def _montar_relatorio(
    jogos: Sequence[Sequence[int]],
    concursos: pd.DataFrame,
    registrar: bool,
) -> Dict[str, object]:
    resultados = conferir_jogos(jogos, concursos)
    if registrar:
        registrar_resultados(resultados)
    log_entretenimento("Simulação histórica")
    total_premios = sum(res.premio_estimado for res in resultados)
    distribuicao = _distribuicao_acertos(resultados)
    return {
        "total_concursos": len(concursos),
        "resultados": [res.__dict__ for res in resultados],
        "distribuicao_acertos": distribuicao,
        "premio_estimado_total": round(total_premios, 2),
    }


def _distribuicao_acertos(resultados: Iterable[ResultadoSimulacao]) -> Dict[int, int]:
    distribuicao: Dict[int, int] = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
    for res in resultados:
        distribuicao[res.acertos] = distribuicao.get(res.acertos, 0) + 1
    return distribuicao


def registrar_resultados(resultados: Iterable[ResultadoSimulacao]) -> None:
    timestamp = datetime.utcnow().isoformat() + "Z"
    registros = [
        ResultadoAposta(
            id_aposta=f"SIM-{res.concurso}-{idx}",
            concurso=res.concurso,
            acertos=res.acertos,
            premio_estimado=res.premio_estimado,
            registrado_em=timestamp,
        )
        for idx, res in enumerate(resultados)
    ]
    if registros:
        salvar_resultados(registros)
