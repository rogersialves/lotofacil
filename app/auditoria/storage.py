"""Armazenamento em CSV para apostas e resultados simulados."""

from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

APOSTAS_PATH = Path("./dados/auditoria/apostas_geradas.csv")
RESULTADOS_PATH = Path("./dados/auditoria/resultados_apostas.csv")


@dataclass
class Aposta:
    id_aposta: str
    origem: str
    dezenas: List[int]
    id_modelo_fechamento: str | None
    n_dezenas_base: int
    score_medio: float | None
    data_geracao: str


def salvar_aposta(aposta: Aposta) -> None:
    """Anexa uma aposta ao CSV correspondente."""

    APOSTAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    existe = APOSTAS_PATH.exists()

    with APOSTAS_PATH.open("a", newline="", encoding="utf8") as arquivo:
        campos = [
            "id_aposta",
            "origem",
            "dezenas",
            "id_modelo_fechamento",
            "n_dezenas_base",
            "score_medio",
            "data_geracao",
        ]
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        if not existe:
            escritor.writeheader()
        registro = asdict(aposta)
        registro["dezenas"] = " ".join(str(d).zfill(2) for d in aposta.dezenas)
        escritor.writerow(registro)


def listar_apostas() -> List[Dict[str, str]]:
    if not APOSTAS_PATH.exists():
        return []
    with APOSTAS_PATH.open("r", encoding="utf8") as arquivo:
        leitor = csv.DictReader(arquivo)
        return list(leitor)


@dataclass
class ResultadoAposta:
    id_aposta: str
    concurso: int
    acertos: int
    premio_estimado: float
    registrado_em: str


def salvar_resultados(resultados: Iterable[ResultadoAposta]) -> None:
    RESULTADOS_PATH.parent.mkdir(parents=True, exist_ok=True)
    existe = RESULTADOS_PATH.exists()
    campos = ["id_aposta", "concurso", "acertos", "premio_estimado", "registrado_em"]

    with RESULTADOS_PATH.open("a", newline="", encoding="utf8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        if not existe:
            escritor.writeheader()
        for resultado in resultados:
            escritor.writerow(asdict(resultado))


def listar_resultados() -> List[Dict[str, str]]:
    if not RESULTADOS_PATH.exists():
        return []
    with RESULTADOS_PATH.open("r", encoding="utf8") as arquivo:
        leitor = csv.DictReader(arquivo)
        return list(leitor)
