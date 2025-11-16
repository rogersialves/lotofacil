from random import choice

from calculos.frequencia import gerar_frequencia
from calculos.faltantes import numeros_faltantes_ciclo


def calcular_pesos(base_dados):
    """
    Calcula o peso de cada dezena.

    :param base_dados: DataFrame da base de dados.

    :return: lista com os pesos(percentual de ocorrncia de cada dezena considerando o ajuste para aquelas
    que so faltantes para completar o ciclo das dezenas).
    """

    frequencia, qtde_sorteios = gerar_frequencia(base_dados)
    ajustes = numeros_faltantes_ciclo(base_dados)

    num_faltantes = ajustes.faltantes
    ajuste_faltantes = ajustes.ajuste_faltantes
    num_restante = ajustes.restantes
    ajuste_restante = ajustes.ajuste_restantes

    fator_distincao = [float('0.000' + str(n)) for n in range(100, 10000)]

    l_peso = list()
    tem_restantes = bool(num_restante)

    for i in range(1, 26):
        if i in num_faltantes:
            peso = (frequencia[i] // 2 + ajuste_faltantes) / qtde_sorteios
        elif tem_restantes and i in num_restante:
            peso = (frequencia[i] // 2 + ajuste_restante) / qtde_sorteios
        else:
            peso = frequencia[i] / qtde_sorteios

        if peso in l_peso:
            l_peso.append(peso + choice(fator_distincao))
        else:
            l_peso.append(peso)

    return l_peso


def calcular_numero_pesos(base_dados):
    """
    Gera um dicionrio contendo os nmeros e os seus pesos.

    :param base_dados: DataFrame da base de dados.

    :return: a relao de nmeros com os seus pesos.
    """

    peso = calcular_pesos(base_dados)

    n_peso = dict()

    for i in range(1, 26):
        n_peso[i] = peso[i - 1]

    return peso, n_peso
