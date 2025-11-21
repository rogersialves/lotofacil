"""Rotas básicas de verificação de status."""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter

from app.core import get_settings

router = APIRouter()


@router.get("/health", summary="Status do backend", response_model=dict)
def healthcheck() -> Dict[str, Any]:
    """
    Retorna metadados do serviço e reforça o caráter de entretenimento do sistema.
    """

    settings = get_settings()
    return {
        "name": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "Ferramenta para análise/entretenimento. "
            "Nenhuma funcionalidade garante prêmios na Lotofácil."
        ),
    }
