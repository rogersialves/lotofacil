from processamento.reajustar_dados import remover_resultado_concursos
from processamento.possibilidades import obter_possibilidades
from processamento.resultados import resultados_ordenados
from calculos.pesos import calcular_numero_pesos
from sorteios.sortear import sortear_numeros
from modelo.modelo import criar_modelo
from dados.dados import carregar_dados
from dados.busca import buscar
import os
import csv
from pandas import DataFrame

# Carrega a base de dados
dados = carregar_dados()

# Inicialização das variáveis
probabilidade = 0.00
predicao_alvo = 0.00
sorteados = list()
procurando = 0
jogos_alta_probabilidade = []  # Lista para armazenar jogos com alta probabilidade

# probabilidade desejada e limite para salvar em CSV
prob_alvo = 99.9
prob_salvar = 97.0  # Probabilidade mínima para salvar em CSV

# Função para salvar jogos em CSV
def salvar_jogos_csv(jogos, caminho="./base/probabilidades.csv"):
    """Salva os jogos de alta probabilidade em um arquivo CSV"""
    modo = 'a' if os.path.exists(caminho) else 'w'
    with open(caminho, modo, newline='') as arquivo:
        escritor = csv.writer(arquivo, delimiter=';')
        # Se for um novo arquivo, escreve o cabeçalho
        if modo == 'w':
            escritor.writerow(['Jogo', 'Probabilidade', 'Acurácia'])
        # Escreve os jogos
        for jogo in jogos:
            escritor.writerow([jogo['sequencia'], jogo['probabilidade'], jogo['acuracia']])
    print(f"\nJogos de alta probabilidade salvos em {caminho}")

# Obtém os pesos de cada dezena e um dicionários com as dezenas e seus pesos
peso, numero_pesos = calcular_numero_pesos(dados)

# Obtém o modelo e sua acuracidade
modelo, pontuacao = criar_modelo(dados)

# Carrega e reajusta os demais dados
print()
print(f'\033[1;33m[Carregando e reajustando os demais dados...]\033[m')
print()

possibilidades = obter_possibilidades()
resultado_concursos = resultados_ordenados(dados)
possibilidades_atualizada = remover_resultado_concursos(
                                                        possibilidades, 
                                                        resultado_concursos
                                                        )
indice_possibilidades = len(possibilidades_atualizada) - 1

if indice_possibilidades < 0:
    raise ValueError('Nenhuma possibilidade disponível para gerar novos jogos.')

# Variável de verificação se o jogo gerado é aceitável
jogo_aceito = False

# Replica até que a probabilidade seja igual à probabilidade desejada
# e o jogo seja aceitável 
while probabilidade < prob_alvo and not jogo_aceito:

    # Atribui a sequência dos números sorteados
    sorteados = sortear_numeros(peso, numero_pesos)
    # Ordena a lista dos números sorteados
    jogo = sorted([numeros[0] for numeros in sorteados])

    # Cria o dataframe com os números sorteados para realizar a predição
    y_alvo = DataFrame(sorteados).iloc[:, 0].to_numpy(dtype='int16')
    y_alvo = y_alvo.reshape(1, 15)

    # Faz a predição da Classe/Alvo e reaproveita o resultado para a probabilidade
    previsao = modelo.predict(y_alvo)
    predicao_alvo = float(previsao.reshape(-1)[0])
    probabilidade = round((predicao_alvo * 100), 1)

    # Verifica se o jogo é possível e se ainda não foi sorteado em algum concurso
    if probabilidade >= prob_alvo:
        indice = buscar(
                        possibilidades_atualizada,
                        0,
                        indice_possibilidades,
                        jogo
                       )
        jogo_aceito = indice is not None
    else:
        jogo_aceito = False

    # Conta quantas vezes procurou a sequência até atingir a probabilidade desejada
    procurando += 1

    # Formata a sequência de números sorteados para ser imprimida na tela
    sequencia = [str(numero[0]).zfill(2) for numero in sorteados]

    # Imprime as informações obtidas no ciclo atual de execução enquanto a probabilidade desejada não foi encontrada
    print(f'Alvo = ({prob_alvo}%) - ACURAC.: {round((pontuacao * 100), 1)}% - Rep.: {str(procurando).zfill(7)}'
          f' - Prob. Enc.: ({str(probabilidade).zfill(2)}%) Sequência: [ ', end='')

    print(*sequencia, ']')

    # Verificar se o jogo tem alta probabilidade para salvar
    if probabilidade >= prob_salvar:
        # Formatar o jogo como string para salvar
        jogo_str = ' '.join(sequencia)
        # Adicionar à lista de jogos de alta probabilidade
        jogos_alta_probabilidade.append({
            'sequencia': jogo_str,
            'probabilidade': probabilidade,
            'acuracia': round((pontuacao * 100), 1)
        })
        print(f"\033[1;32m[Jogo com {probabilidade}% de probabilidade adicionado à lista]\033[m")

    # Se o jogo não é aceitável, zera a probabilidade para gerar novo jogo
    if not jogo_aceito:
        probabilidade = 0.0

# Após o loop, salvar os jogos de alta probabilidade (se houver)
if jogos_alta_probabilidade:
    salvar_jogos_csv(jogos_alta_probabilidade)

# Resultados
print(f'\nAcuracidade do Modelo: {round((pontuacao * 100), 1)}%')

print('\n0 = Não tem chance de ganhar | 1 = Tem chance de ganhar')
print(f'Resultado: (Previsão Modelo) = {predicao_alvo}')

print(f'\nProbabilidade das dezenas sairem: {probabilidade}%')

# Números sorteados (em ordem de sorteio e em ordem crescente)
print(f'\nNúmeros sorteados:  {[numeros[0] for numeros in sorteados]}')
print(f'\nNúmeros ordenados:  {jogo}')
