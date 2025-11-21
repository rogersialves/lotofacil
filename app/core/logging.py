"""Configuração central de logging com alertas de entretenimento."""

import logging
from typing import Optional

LOGGER = logging.getLogger("lotofacil")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)


def log_entretenimento(contexto: Optional[str] = None) -> None:
    mensagem = "Uso destinado a análise/entretenimento. Não há garantia de prêmios."
    if contexto:
        mensagem = f"{contexto} — {mensagem}"
    LOGGER.warning(mensagem)
