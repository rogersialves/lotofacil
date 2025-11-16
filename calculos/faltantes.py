from dataclasses import dataclass
from typing import List

from calculos.frequencia import gerar_frequencia
from random import choice, choices


@dataclass
class AjusteDezenas:
    faltantes: List[int]
    ajuste_faltantes: int
    restantes: List[int]
    ajuste_restantes: int


def ultimo_jogos(base_dados):
    """
    Encontra a quantidade de jogos realizados posteriormente ao ltimo ciclo fechado.

    :param base_dados: DataFrame da base de dados.

    :return: a quantidade de jogos.
    """

    # Carrega a base de dados
    dados = base_dados.copy()

    # O maior ciclo fechado
    maior = max(dados['Ciclo'])

    # 4ndice do ltimo ciclo fechado
    ciclo = int(dados.query(f'Ciclo == {maior}')['Concurso'].index[0])

    # Quantidade de jogos realizados ap3s o ltimo ciclo fechado
    jogos = len(dados.iloc[ciclo + 1:])

    return jogos


def numeros_faltantes_ciclo(base_dados):
    """
    Obtem o(s) n9mero(s) faltante(s) para fechar o ciclo das dezenas.

    :param base_dados: DataFrame da base de dados.

    :return: o(s) n9mero(s) faltante(s) sorteado(s) e o percentual de reajuste de peso.
    """

    dados = base_dados.copy()
    jogos = ultimo_jogos(dados)
    frequencia = gerar_frequencia(dados)

    maior_peso = next(iter(frequencia[0].values()), 0)

    relacao_numeros = list(dados.iloc[-1, 22:32].values)
    num_faltantes = [numero for numero in relacao_numeros if numero > 0]
    qtde_faltantes = len(num_faltantes)

    ajuste_padrao = AjusteDezenas(num_faltantes, maior_peso, [], 0)

    if not qtde_faltantes:
        return ajuste_padrao

    if jogos == 1:
        jogo = list(range(1, 8))
        pesos = [len(dados.query(f'Jogo == 2 & Falta == {i}')) for i in jogo]
        n_dz = choices(jogo, weights=pesos, k=1)

        numeros = num_faltantes[:]
        faltantes = list()

        for _ in range(n_dz[0]):
            if not numeros:
                break
            numero_sorteado = choice(numeros)
            numeros.remove(numero_sorteado)
            faltantes.append(numero_sorteado)

        restantes = [numero for numero in num_faltantes if numero not in faltantes]

        return AjusteDezenas(faltantes, maior_peso, restantes, maior_peso // 2)

    if jogos in (2, 3, 4):
        referencia = jogos + 1
        jogo = list(range(0, qtde_faltantes + 1))
        pesos = [len(dados.query(f'Jogo == {referencia} & Falta == {i}')) for i in jogo]
        n_dz = choices(jogo, weights=pesos, k=1)

        numeros = num_faltantes[:]
        faltantes = list()

        for _ in range(n_dz[0]):
            if not numeros:
                break
            numero_sorteado = choice(numeros)
            numeros.remove(numero_sorteado)
            faltantes.append(numero_sorteado)

        if qtde_faltantes == n_dz[0] or n_dz[0] == 0:
            return ajuste_padrao

        if 1 < qtde_faltantes != n_dz[0] and n_dz[0] > 0:
            restantes = [numero for numero in num_faltantes if numero not in faltantes]
            return AjusteDezenas(faltantes, maior_peso, restantes, maior_peso // 2)

        return ajuste_padrao

    return ajuste_padrao
