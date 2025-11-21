"""Inicialização das rotas públicas da API."""

from fastapi import APIRouter

from app.api.routes import auditoria, dados, fechamentos, health, ia, simulacoes

api_router = APIRouter()

api_router.include_router(
    health.router,
    prefix="/status",
    tags=["status"],
)
api_router.include_router(
    dados.router,
    prefix="/dados",
    tags=["dados"],
)
api_router.include_router(
    fechamentos.router,
    prefix="/fechamentos",
    tags=["fechamentos"],
)
api_router.include_router(
    ia.router,
    prefix="/ia",
    tags=["ia"],
)
api_router.include_router(
    simulacoes.router,
    prefix="/simulacoes",
    tags=["simulacoes"],
)
api_router.include_router(
    auditoria.router,
    prefix="/auditoria",
    tags=["auditoria"],
)

__all__ = ["api_router"]
