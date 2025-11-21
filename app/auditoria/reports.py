"""Geração de relatórios a partir das tabelas de auditoria."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Dict, List

from app.auditoria.storage import APOSTAS_PATH, RESULTADOS_PATH


def relatorio_apostas() -> Dict[str, object]:
    if not APOSTAS_PATH.exists():
        return {"total": 0, "por_origem": {}}
    with APOSTAS_PATH.open("r", encoding="utf8") as arquivo:
        leitor = csv.DictReader(arquivo)
        origens = Counter()
        total = 0
        for linha in leitor:
            total += 1
            origens[linha.get("origem", "desconhecida")] += 1
    return {"total": total, "por_origem": dict(origens)}


def relatorio_resultados() -> Dict[str, object]:
    if not RESULTADOS_PATH.exists():
        return {"total": 0, "por_faixa": {}, "premio_estimado_total": 0.0}
    with RESULTADOS_PATH.open("r", encoding="utf8") as arquivo:
        leitor = csv.DictReader(arquivo)
        faixas = Counter()
        total = 0
        premio = 0.0
        for linha in leitor:
            acertos = int(linha.get("acertos", 0))
            faixas[acertos] += 1
            total += 1
            premio += float(linha.get("premio_estimado", 0))
    return {
        "total": total,
        "por_faixa": dict(sorted(faixas.items(), reverse=True)),
        "premio_estimado_total": round(premio, 2),
    }
