from pandas import read_csv

URL = "./base/resultados.csv"
DEZENAS = [i for i in range(1, 26)]


def criar_nao_sorteados(
    dz=DEZENAS,
    base_url=URL,
    base_lista=None,
    atualizar_base_resultados=False,
):
    """
    Retorna lista com as dezenas não sorteadas em cada concurso.
    """

    if base_lista is not None and isinstance(base_lista, list):
        nao_sorteados = []
        for resultado in base_lista:
            resultado.sort()
            diferenca = set(dz).difference(resultado)
            nao_sorteados.append(list(diferenca))
        return nao_sorteados

    if atualizar_base_resultados:
        # Atualiza o CSV com todos os resultados dos sorteios já realizados
        from dados import scrapping_resultados

        scrapping_resultados.atualizar_resultados()

    dados = read_csv(base_url, sep=";", encoding="utf-8")
    resultados = dados.iloc[:, 2:17].values

    nao_sorteados = []
    for resultado in resultados:
        resultado.sort()
        diferenca = set(dz).difference(resultado)
        nao_sorteados.append(list(diferenca))

    return nao_sorteados
