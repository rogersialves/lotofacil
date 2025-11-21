"""Registro simples das execuções de modelos."""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import json

REGISTRY_PATH = Path("./models/registry.json")


@dataclass
class ExecucaoModelo:
    id_modelo: str
    tipo: str
    caminho_modelo: str
    dataset: str
    metricas: Dict[str, float]
    data_treino: str


def registrar_execucao(execucao: ExecucaoModelo) -> None:
    """Adiciona uma nova execução ao registro."""

    registros = listar_execucoes()
    registros.append(asdict(execucao))
    REGISTRY_PATH.write_text(
        json.dumps(registros, ensure_ascii=False, indent=2),
        encoding="utf8",
    )


def listar_execucoes() -> List[Dict[str, object]]:
    """Retorna o histórico de execuções."""

    if not REGISTRY_PATH.exists():
        return []
    return json.loads(REGISTRY_PATH.read_text(encoding="utf8"))


def nova_execucao(
    id_modelo: str,
    tipo: str,
    caminho_modelo: Path,
    dataset: str,
    metricas: Dict[str, float],
) -> ExecucaoModelo:
    return ExecucaoModelo(
        id_modelo=id_modelo,
        tipo=tipo,
        caminho_modelo=str(caminho_modelo),
        dataset=dataset,
        metricas=metricas,
        data_treino=datetime.utcnow().isoformat() + "Z",
    )
