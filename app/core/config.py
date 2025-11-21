"""Definição centralizada de configurações do backend."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Valores padrão para configuração da API."""

    app_name: str = "Loterias Caixa – Plataforma IA"
    description: str = (
        "Serviços backend para análises, IA e fechamentos da Lotofácil. "
        "Uso exclusivo para entretenimento: não há garantias de ganho."
    )
    version: str = "0.1.0"
    environment: str = os.getenv("APP_ENV", "development")
    api_prefix: str = "/api"
    docs_url: str = "/api/docs"
    openapi_url: str = "/api/openapi.json"


_SETTINGS = Settings()


def get_settings() -> Settings:
    """Retorna instância singleton com as configurações da aplicação."""

    return _SETTINGS
