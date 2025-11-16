from typing import Any

from dados.dados import dividir_dados
import keras
from keras import layers, models, callbacks

SILENT: Any = 0


def criar_modelo(
                    base_dados, 
                    primeira_camada=30,
                    segunda_camada=15,
                    terceira_camada=15,
                    saida=1,
                    periodo=50,
                    lote=15
                ):
    """
    Cria o modelo sequêncial com três camadas.

    :param base_dados: DataFrame da base de dados.
    :param primeira_camada: camada de entrada utilizando a função retificadora (relu). Default: 30 neurônios.
    :param segunda_camada: segunda camada utilizando a função retificadora(relu). Default: 15 neurônios.
    :param terceira_camada: terceira camada utilizando a função retificadora (relu). Default 15 neurônios.
    :param saida: camada de saída utilizando a função de ativação (sigmoid). Default: 1 neurônio.
    :param periodo: quantidade de iterações para ajuste do modelo.
    :param lote: ajuste do número de instâncias.
    :return: o modelo gerado.
    """

    x_treino, x_teste, y_treino, y_teste, atributos = dividir_dados(base_dados)

    # Criando o modelo
    modelo = models.Sequential()

    # Criando as camadas do modelo
    modelo.add(layers.Dense(primeira_camada, input_dim=atributos, activation='relu'))
    modelo.add(layers.Dense(segunda_camada, activation='relu'))
    modelo.add(layers.Dense(terceira_camada, activation='relu'))
    modelo.add(layers.Dense(saida, activation='sigmoid'))

    # Compilando o modelo
    modelo.compile(
                    loss='binary_crossentropy',
                    optimizer='adam',
                    metrics=['accuracy'])

    # Configurando EarlyStopping
    early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    # Treinando o modelo (com verbose=0 para suprimir saídas)
    modelo.fit(
                x_treino,
                y_treino,
                epochs=periodo,
                batch_size=lote,
                verbose=SILENT,
                validation_split=0.2,
                callbacks=[early_stopping]
              )

    # Avaliação do modelo
    pontuacao = modelo.evaluate(x_teste, y_teste, verbose=SILENT)

    print(f"Dimensão da entrada do modelo: {atributos}")

    return modelo, pontuacao[1]

