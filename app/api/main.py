"""Aplicação FastAPI principal."""

from fastapi import FastAPI

from app.api import api_router
from app.core import get_settings


def create_app() -> FastAPI:
    """Instancia a aplicação FastAPI com configurações padrão."""

    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.version,
        docs_url=settings.docs_url,
        openapi_url=settings.openapi_url,
    )

    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
