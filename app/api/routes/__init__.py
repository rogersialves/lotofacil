"""Coleção de rotas/blueprints expostas pela API."""

from app.api.routes import auditoria, dados, fechamentos, health, ia, simulacoes

__all__ = ["auditoria", "dados", "fechamentos", "health", "ia", "simulacoes"]
