"""Persistência simples de apostas geradas e resultados."""

from app.auditoria.storage import (
    Aposta,
    ResultadoAposta,
    salvar_aposta,
    salvar_resultados,
    listar_apostas,
    listar_resultados,
)
from app.auditoria.reports import relatorio_apostas, relatorio_resultados

__all__ = [
    "Aposta",
    "ResultadoAposta",
    "salvar_aposta",
    "salvar_resultados",
    "listar_apostas",
    "listar_resultados",
    "relatorio_apostas",
    "relatorio_resultados",
]
