"""Geração de universos de dezenas usando o fluxo neural legado (>=98% de acurácia)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional
import csv

import pandas as pd

from calculos.pesos import calcular_numero_pesos
from dados.dados import carregar_dados
from dados.busca import buscar
from modelo.modelo import criar_modelo
from processamento.possibilidades import obter_possibilidades
from processamento.resultados import resultados_ordenados
from processamento.reajustar_dados import remover_resultado_concursos
from sorteios.sortear import sortear_numeros


TESTE_PATH = Path("./base/testes_fechamentos.csv")


@dataclass
class UniversoGerado:
    dezenas: List[int]
    pontuacao_modelo: float
    probabilidade_jogo: float
    iteracoes: int
    timestamp: str
    acuracia_alvo: float
    probabilidade_alvo: float


def gerar_universo_neural(
    n_dezenas: int,
    acuracia_min: float = 0.98,
    probabilidade_min: float = 99.0,
    max_iteracoes: int = 200000,
    max_retreinos: int = 20,
    progresso: Optional[Callable[[str], None]] = None,
) -> UniversoGerado:
    """
    Recria a lógica original (jogar.py) para gerar universos com apoio da rede neural.
    """

    if n_dezenas < 15 or n_dezenas > 21:
        raise ValueError("O universo deve conter entre 15 e 21 dezenas.")

    dados = carregar_dados()
    modelo = None
    pontuacao = 0.0
    for tentativa in range(1, max_retreinos + 1):
        modelo, pontuacao = criar_modelo(dados)
        if progresso:
            progresso(f"Treinamento {tentativa}/{max_retreinos} – acurácia {pontuacao*100:.2f}%")
        if pontuacao >= acuracia_min:
            break
    else:
        raise RuntimeError(
            f"Não foi possível atingir a acurácia solicitada ({acuracia_min*100:.2f}%) "
            f"após {max_retreinos} treinos (melhor {pontuacao*100:.2f}%). "
            "Reduza o alvo ou execute um treinamento manual."
        )

    peso, numero_pesos = calcular_numero_pesos(dados)
    possibilidades = obter_possibilidades()
    resultado_concursos = resultados_ordenados(dados)
    possibilidades_atualizadas = remover_resultado_concursos(possibilidades, resultado_concursos)
    indice_possibilidades = len(possibilidades_atualizadas) - 1
    if indice_possibilidades < 0:
        raise RuntimeError("Não há possibilidades disponíveis para gerar novos universos.")

    probabilidade = 0.0
    jogo_aceito = False
    iteracoes = 0
    sequencia = []

    while probabilidade < probabilidade_min or not jogo_aceito:
        iteracoes += 1
        if iteracoes > max_iteracoes:
            raise RuntimeError("Número máximo de tentativas excedido ao buscar universo válido.")

        sorteados = sortear_numeros(peso, numero_pesos)
        jogo = sorted([numeros[0] for numeros in sorteados])

        y_alvo = pd.DataFrame(sorteados).iloc[:, 0].to_numpy(dtype="int16")
        y_alvo = y_alvo.reshape(1, 15)
        previsao = modelo.predict(y_alvo, verbose=0)
        predicao_alvo = float(previsao.reshape(-1)[0])
        probabilidade = round(predicao_alvo * 100, 2)

        if progresso and iteracoes % 200 == 0:
            progresso(
                f"Tentativa {iteracoes}: probabilidade atual {probabilidade:.2f}% "
                f"(alvo {probabilidade_min}%); universo {'aceito' if jogo_aceito else 'em busca'}."
            )

        if probabilidade >= probabilidade_min:
            indice = buscar(
                possibilidades_atualizadas,
                0,
                indice_possibilidades,
                jogo,
            )
            jogo_aceito = indice is not None
            if jogo_aceito:
                sequencia = jogo
        else:
            jogo_aceito = False

    dezenas_universo = sequencia.copy()
    if n_dezenas > 15:
        extras = [
            (dezena, numero_pesos[dezena])
            for dezena in range(1, 26)
            if dezena not in dezenas_universo
        ]
        extras.sort(key=lambda item: item[1], reverse=True)
        dezenas_universo.extend([dezena for dezena, _ in extras[: n_dezenas - 15]])
        dezenas_universo = sorted(dezenas_universo)

    if progresso:
        progresso(
            f"Universo encontrado após {iteracoes} tentativas "
            f"(probabilidade {probabilidade:.2f}%, acurácia alcançada {pontuacao*100:.2f}%)."
        )

    return UniversoGerado(
        dezenas=dezenas_universo,
        pontuacao_modelo=round(pontuacao, 4),
        probabilidade_jogo=probabilidade,
        iteracoes=iteracoes,
        timestamp=datetime.utcnow().isoformat() + "Z",
        acuracia_alvo=acuracia_min,
        probabilidade_alvo=probabilidade_min,
    )


def registrar_teste_fechamento(
    id_modelo: str,
    universo: UniversoGerado,
    garantia: str,
    total_jogos: int,
) -> Path:
    TESTE_PATH.parent.mkdir(parents=True, exist_ok=True)
    existe = TESTE_PATH.exists()
    campos = [
        "timestamp",
        "id_modelo",
        "universo_dezenas",
        "garantia",
        "pontuacao_modelo",
        "probabilidade_jogo",
        "iteracoes",
        "total_jogos",
        "acuracia_alvo",
        "probabilidade_alvo",
    ]

    with TESTE_PATH.open("a", newline="", encoding="utf8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=campos)
        if not existe:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": universo.timestamp,
                "id_modelo": id_modelo,
                "universo_dezenas": " ".join(str(d).zfill(2) for d in universo.dezenas),
                "garantia": garantia,
                "pontuacao_modelo": f"{universo.pontuacao_modelo:.4f}",
                "probabilidade_jogo": f"{universo.probabilidade_jogo:.2f}",
                "iteracoes": universo.iteracoes,
                "total_jogos": total_jogos,
                "acuracia_alvo": f"{universo.acuracia_alvo:.4f}",
                "probabilidade_alvo": f"{universo.probabilidade_alvo:.2f}",
            }
        )

    return TESTE_PATH
