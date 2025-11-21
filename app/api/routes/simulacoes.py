"""Endpoints para simulações e conferências de estratégias."""

from typing import List, Sequence

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field, validator

from app.simulacoes import simular_intervalo, simular_ultimos

router = APIRouter()


class SimulacaoRequest(BaseModel):
    jogos: List[Sequence[int]]
    ultimos: int = Field(200, ge=1, le=2000, description="Quantidade de concursos mais recentes para o backtest.")
    atualizar: bool = False
    registrar: bool = False

    @validator("jogos")
    def validar_jogos(cls, jogos: List[Sequence[int]]) -> List[Sequence[int]]:
        if not jogos:
            raise ValueError("Informe pelo menos um jogo para simulação.")
        for jogo in jogos:
            if len(jogo) != 15:
                raise ValueError("Cada jogo deve conter exatamente 15 dezenas.")
            if len(set(jogo)) != 15:
                raise ValueError("As dezenas de cada jogo devem ser únicas.")
            for dezena in jogo:
                if not 1 <= dezena <= 25:
                    raise ValueError("As dezenas devem estar entre 1 e 25.")
        return jogos


@router.post(
    "/estrategia",
    summary="Simula o desempenho de uma estratégia em concursos recentes",
)
def simular_estrategia_endpoint(payload: SimulacaoRequest = Body(...)):
    try:
        resultado = simular_ultimos(
            jogos=payload.jogos,
            ultimos=payload.ultimos,
            atualizar=payload.atualizar,
            registrar=payload.registrar,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        **resultado,
        "disclaimer": "Simulação histórica para entretenimento; não garante resultados futuros.",
    }
