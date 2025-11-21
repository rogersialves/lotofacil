"""Pipeline de treinamento do modelo por jogo."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
import joblib

from app.features import preparar_dataset_jogo
from app.ml import registry

MODELO_PATH = Path("./models/jogo/model.joblib")


def treinar_modelo_jogo(atualizar: bool = False) -> Dict[str, float]:
    dataset_real = preparar_dataset_jogo(atualizar=atualizar)
    dataset_real["label"] = 1

    # Cria combinações artificiais permutando colunas para gerar classe 0
    artificiais = dataset_real.copy()
    artificiais.iloc[:, 1:26] = artificiais.iloc[:, 1:26].sample(frac=1).values
    artificiais["label"] = 0

    dataset = pd.concat([dataset_real, artificiais], ignore_index=True)
    atributos = dataset.drop(columns=["label", "concurso"])
    alvo = dataset["label"]

    x_treino, x_teste, y_treino, y_teste = train_test_split(
        atributos, alvo, test_size=0.2, random_state=42, stratify=alvo
    )

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(x_treino, y_treino)
    y_prob = modelo.predict_proba(x_teste)[:, 1]
    metricas = {"auc": round(roc_auc_score(y_teste, y_prob), 4)}

    MODELO_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, MODELO_PATH)

    execucao = registry.nova_execucao(
        id_modelo="modelo_jogo_rf",
        tipo="jogo",
        caminho_modelo=MODELO_PATH,
        dataset="dataset_jogo",
        metricas=metricas,
    )
    registry.registrar_execucao(execucao)
    return metricas


def carregar_modelo_jogo():
    if not MODELO_PATH.exists():
        raise FileNotFoundError("Modelo por jogo ainda não foi treinado.")
    return joblib.load(MODELO_PATH)
