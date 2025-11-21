from pandas import read_csv

from processamento.possibilidades import obter_possibilidades
from processamento.reajustar_dados import obter_indices

ARQUIVO = "./base/resultados.csv"


def dados_indice(atualizar_base_resultados=False):
    """
    Cria DataFrame com concurso, índice na lista de possibilidades e metadados.
    """

    if atualizar_base_resultados:
        from dados import scrapping_resultados

        scrapping_resultados.atualizar_resultados()

    resultado_concurso = read_csv(ARQUIVO, sep=";", encoding="utf-8")

    num_sorteados = resultado_concurso.iloc[:, 2:17]
    num_ordenados = num_sorteados.values
    for numeros in num_ordenados:
        numeros.sort()

    resultados = num_ordenados.tolist()
    possibilidades = obter_possibilidades()
    indices = obter_indices(possibilidades, resultados)

    dados = resultado_concurso[["Concurso", "Data Sorteio", "Ganhou"]].copy()
    dia = dados["Data Sorteio"].apply(lambda data: data[0:2])
    mes = dados["Data Sorteio"].apply(lambda data: data[3:5])
    ano = dados["Data Sorteio"].apply(lambda data: data[-4:])

    dados.insert(1, "Indice", indices)
    dados.insert(len(dados.columns), column="Dia", value=dia)
    dados.insert(len(dados.columns), column="Mes", value=mes)
    dados.insert(len(dados.columns), column="Ano", value=ano)

    return dados
