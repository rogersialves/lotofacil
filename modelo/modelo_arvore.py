from dados.dados import dividir_dados
from sklearn.ensemble import RandomForestClassifier 
import numpy as np

def criar_modelo(
                base_dados, 
                n_estimadores=100,
                **kwargs
            ):
    """
    Cria um modelo RandomForest.
    
    :param base_dados: DataFrame da base de dados.
    :param n_estimadores: Número de árvores. Default: 100.
    :return: o modelo gerado e sua pontuação.
    """
    x_treino, x_teste, y_treino, y_teste, atributos = dividir_dados(base_dados)
    
    # Criando o modelo
    modelo = RandomForestClassifier(n_estimators=n_estimadores, random_state=42)
    
    # Treinando o modelo
    modelo.fit(x_treino, y_treino)
    
    # Avaliação
    pontuacao = modelo.score(x_teste, y_teste)
    
    # Adicionando método predict compatível com formato do Keras
    original_predict = modelo.predict_proba
    
    def keras_like_predict(X):
        probs = original_predict(X)
        return probs
    
    modelo.predict = keras_like_predict
    
    return modelo, pontuacao