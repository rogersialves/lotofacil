"""Pipeline de treinamento do modelo por dezena."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
import joblib

from app.features import DatasetConfig, preparar_dataset_dezena
from app.ml import registry

MODELO_PATH = Path("./models/dezena/model.joblib")


def treinar_modelo_dezena(atualizar: bool = False) -> Dict[str, float]:
    dataset = preparar_dataset_dezena(atualizar=atualizar, config=DatasetConfig())
    atributos = dataset.drop(columns=["sorteada"])
    alvo = dataset["sorteada"]

    x_treino, x_teste, y_treino, y_teste = train_test_split(
        atributos, alvo, test_size=0.2, random_state=42, stratify=alvo
    )

    modelo = LogisticRegression(max_iter=500)
    modelo.fit(x_treino, y_treino)

    y_pred = modelo.predict(x_teste)
    y_prob = modelo.predict_proba(x_teste)[:, 1]
    metricas = {
        "accuracy": round(accuracy_score(y_teste, y_pred), 4),
        "auc": round(roc_auc_score(y_teste, y_prob), 4),
    }

    MODELO_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, MODELO_PATH)

    execucao = registry.nova_execucao(
        id_modelo="modelo_dezena_lr",
        tipo="dezena",
        caminho_modelo=MODELO_PATH,
        dataset="dataset_dezena",
        metricas=metricas,
    )
    registry.registrar_execucao(execucao)
    return metricas


def carregar_modelo_dezena():
    if not MODELO_PATH.exists():
        raise FileNotFoundError("Modelo por dezena ainda não foi treinado.")
    return joblib.load(MODELO_PATH)
