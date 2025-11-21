"""Endpoints para exposição pública dos dados históricos."""

from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.etl import ConcursoFiltro, carregar_estatisticas, listar_concursos
from app.features import calcular_estatisticas_avancadas

router = APIRouter()


@router.get(
    "/concursos",
    summary="Lista concursos da Lotofácil",
    response_model=List[dict],
)
def listar_concursos_endpoint(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    formato: str = Query("wide", pattern="^(wide|long)$"),
    atualizar: bool = Query(False, description="Força atualização do histórico antes de listar."),
):
    filtro = ConcursoFiltro(limit=limit, offset=offset, formato=formato, atualizar=atualizar)
    registros = listar_concursos(filtro)
    if not registros and offset > 0:
        raise HTTPException(status_code=404, detail="Offset além do total de concursos.")
    return registros


@router.get(
    "/estatisticas/dezenas",
    summary="Retorna estatísticas básicas das dezenas",
    response_model=dict,
)
def estatisticas_dezenas_endpoint(
    atualizar: bool = Query(False, description="Atualiza dados antes de retornar as estatísticas."),
):
    return carregar_estatisticas(atualizar=atualizar)


@router.get(
    "/estatisticas/avancadas",
    summary="Estatísticas avançadas (freq. móveis, atrasos, pares/ímpares)",
    response_model=dict,
)
def estatisticas_avancadas_endpoint(
    atualizar: bool = Query(False, description="Atualiza dados antes de computar as estatísticas."),
):
    return calcular_estatisticas_avancadas(atualizar=atualizar)
