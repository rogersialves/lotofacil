"""Endpoints para consultar histórico de apostas e resultados."""

from typing import List, Optional

from fastapi import APIRouter, Query

from app.auditoria.storage import listar_apostas, listar_resultados
from app.auditoria.reports import relatorio_apostas, relatorio_resultados

router = APIRouter()


@router.get(
    "/apostas",
    summary="Lista apostas geradas registradas pelo sistema",
    response_model=List[dict],
)
def listar_apostas_endpoint(
    origem: Optional[str] = Query(None, description="Filtra por origem (ex.: fechamento, IA, manual)."),
    modelo: Optional[str] = Query(None, description="Filtra por id_modelo_fechamento."),
):
    apostas = listar_apostas()
    if origem:
        apostas = [aposta for aposta in apostas if aposta.get("origem") == origem]
    if modelo:
        apostas = [
            aposta
            for aposta in apostas
            if aposta.get("id_modelo_fechamento") == modelo
        ]
    return apostas


@router.get(
    "/resultados",
    summary="Lista resultados registrados nas simulações e conferências",
    response_model=List[dict],
)
def listar_resultados_endpoint(
    min_acertos: int = Query(11, ge=0, le=15, description="Retorna somente resultados com acertos >= min_acertos."),
):
    resultados = listar_resultados()
    return [
        resultado
        for resultado in resultados
        if int(resultado.get("acertos", 0)) >= min_acertos
    ]


@router.get(
    "/relatorios",
    summary="Resumo agregado das apostas e resultados registrados",
)
def relatorios_auditoria():
    return {
        "apostas": relatorio_apostas(),
        "resultados": relatorio_resultados(),
        "disclaimer": "Relatórios baseados em dados históricos registrados localmente.",
    }
