"""Serviços simplificados de IA/heurísticas para sugestão e scoring."""

from app.ia.services import sugerir_dezenas, score_jogos
from app.ia.strategy import sugerir_estrategias

__all__ = ["sugerir_dezenas", "score_jogos", "sugerir_estrategias"]
