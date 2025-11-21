"""Disponibiliza os pipelines de treinamento."""

from app.ml.pipelines.dezena import treinar_modelo_dezena
from app.ml.pipelines.jogo import treinar_modelo_jogo

__all__ = ["treinar_modelo_dezena", "treinar_modelo_jogo"]
