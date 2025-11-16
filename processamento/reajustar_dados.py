from dados.busca import buscar


def _obter_indices_validos(possibilidades, resultado_concursos):
	"""
	Busca os ��ndices das combina����es informadas e garante que todos foram encontrados.
	"""
	elem_ini = 0
	elem_fin = len(possibilidades) - 1

	indices = list()
	nao_encontrados = list()

	for valor_busca in resultado_concursos:
		indice = buscar(
                          possibilidades,
                          elem_ini,
                          elem_fin,
                          valor_busca
                         )
		if indice is None:
			nao_encontrados.append(valor_busca)
		else:
			indices.append(indice)

	if nao_encontrados:
		exemplos = ', '.join(str(seq) for seq in nao_encontrados[:3])
		raise ValueError(
						f'{len(nao_encontrados)} resultado(s) n�o encontrados na lista de possibilidades. '
						f'Exemplos: {exemplos}'
						)

	return indices


def remover_resultado_concursos(possibilidades, resultado_concursos):
	"""
	Remove da lista de possibilidades os resultados já sorteados.
	
	:param possibilidades: Combinações possíveis da Lotofácil
	:param resultado_concursos: Resultado de todos os concursos
	
	return:	A lista de possibilidades sem os resultados já sorteados.
	"""
	from pandas import Series

	indices = _obter_indices_validos(possibilidades, resultado_concursos)

	if not indices:
		return possibilidades

	s_possibilidades = Series(possibilidades)
	removidos = s_possibilidades.drop(indices)

	lista_possibilidades_atualizada = removidos.values 
	
	return lista_possibilidades_atualizada.tolist()


def obter_indices(possibilidades, resultado_concursos):
	"""
	Obtém os índices da lista de possibilidades dos resultados já sorteados.
	
	:param possibilidades: Combinações possíveis da Lotofácil
	:param resultado_concursos: Resultado de todos os concursos
	
	return:	Uma lista com os índice dos resultados já sorteados nos concursos.
	"""
	return _obter_indices_validos(possibilidades, resultado_concursos)
