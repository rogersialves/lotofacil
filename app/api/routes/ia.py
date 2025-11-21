"""Endpoints de IA (heurísticas) para sugestão e scoring."""

from typing import List, Sequence

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from app.ia import score_jogos as score_jogos_service
from app.ia import sugerir_dezenas as sugerir_dezenas_service
from app.ia import sugerir_estrategias as sugerir_estrategias_service

router = APIRouter()


class SugerirDezenasRequest(BaseModel):
    n_dezenas: int = Field(ge=15, le=21)
    modo: str = Field(default="mix", pattern="^(probabilidade|atraso|mix)$")
    atualizar: bool = False


@router.post(
    "/sugerir_dezenas",
    summary="Sugere dezenas com base em heurísticas de frequência/atraso",
)
def sugerir_dezenas_endpoint(payload: SugerirDezenasRequest = Body(...)):
    try:
        return sugerir_dezenas_service(
            n_dezenas=payload.n_dezenas,
            modo=payload.modo,
            atualizar=payload.atualizar,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class ScoreJogosRequest(BaseModel):
    jogos: List[Sequence[int]]
    atualizar: bool = False


@router.post(
    "/score_jogos",
    summary="Calcula um score heurístico para cada jogo informado",
)
def score_jogos_endpoint(payload: ScoreJogosRequest = Body(...)):
    try:
        return {
            "resultados": score_jogos_service(payload.jogos, atualizar=payload.atualizar),
            "disclaimer": "Pontuação heurística baseada em históricos. Uso recreativo.",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class SugerirEstrategiaRequest(BaseModel):
    orçamento: float = Field(..., gt=0)
    perfil: str = Field(default="balanceado", pattern="^(conservador|balanceado|agressivo)$")
    atualizar: bool = False
    limite: int = Field(default=5, ge=1, le=20)


@router.post(
    "/sugerir_n_dezenas",
    summary="Sugere pares (n_dezenas, modelo de fechamento) com base no orçamento/perfil",
)
def sugerir_n_dezenas_endpoint(payload: SugerirEstrategiaRequest = Body(...)):
    estrategias = sugerir_estrategias_service(
        orçamento=payload.orçamento,
        perfil=payload.perfil,
        atualizar=payload.atualizar,
        limite=payload.limite,
    )
    if estrategias.empty:
        return {"resultados": [], "mensagem": "Nenhuma estratégia encontrada dentro do orçamento."}
    return {
        "resultados": estrategias.to_dict(orient="records"),
        "disclaimer": "Sugestões baseadas em dados históricos; não garantem retorno financeiro.",
    }
