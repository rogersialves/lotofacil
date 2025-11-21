"""Endpoints para catálogo e geração de fechamentos."""

from dataclasses import asdict
from datetime import datetime
from typing import List

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, Field, validator

from app.fechamentos import aplicar_fechamento, listar_modelos, obter_modelo
from app.ia import score_jogos
from app.auditoria import salvar_aposta, Aposta

router = APIRouter()


@router.get(
    "/modelos",
    summary="Lista modelos de fechamento suportados",
    response_model=List[dict],
)
def listar_modelos_endpoint(
    n_dezenas: int = Query(None, ge=15, le=21, description="Filtra modelos por quantidade de dezenas."),
):
    modelos = listar_modelos()
    if n_dezenas is not None:
        modelos = [modelo for modelo in modelos if modelo.n_dezenas == n_dezenas]
    registros = []
    for modelo in modelos:
        registro = asdict(modelo)
        registro["preco_total"] = modelo.preco_total
        registros.append(registro)
    return registros


class GerarFechamentoRequest(BaseModel):
    id_modelo: str = Field(..., description="Identificador do modelo de fechamento.")
    dezenas: List[int] = Field(..., description="Dezenas escolhidas pelo usuário.")
    ordenar_por_score: bool = True
    limitar_top: int | None = Field(
        default=None,
        ge=1,
        description="Se informado, mantém apenas os primeiros jogos após ordenação.",
    )
    atualizar_stats: bool = False

    @validator("dezenas")
    def validar_dezenas(cls, value: List[int]) -> List[int]:
        if len(value) != len(set(value)):
            raise ValueError("As dezenas não podem se repetir.")
        for dezena in value:
            if not 1 <= dezena <= 25:
                raise ValueError("As dezenas devem estar entre 1 e 25.")
        return value


@router.post(
    "/gerar",
    summary="Aplica o fechamento às dezenas escolhidas",
)
def gerar_fechamento_endpoint(payload: GerarFechamentoRequest = Body(...)):
    try:
        modelo = obter_modelo(payload.id_modelo)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if len(payload.dezenas) != modelo.n_dezenas:
        raise HTTPException(
            status_code=400,
            detail=f"Modelo {modelo.id_modelo} requer {modelo.n_dezenas} dezenas.",
        )

    jogos = aplicar_fechamento(payload.dezenas, payload.id_modelo)
    resultados = score_jogos(jogos, atualizar=payload.atualizar_stats)

    if payload.ordenar_por_score:
        resultados = sorted(resultados, key=lambda item: item["score"], reverse=True)

    if payload.limitar_top:
        resultados = resultados[: payload.limitar_top]

    modelo_dict = asdict(modelo)
    modelo_dict["preco_total"] = modelo.preco_total
    timestamp = datetime.utcnow().isoformat() + "Z"

    aposta = Aposta(
        id_aposta=f"{payload.id_modelo}-{timestamp}",
        origem="fechamento",
        dezenas=payload.dezenas,
        id_modelo_fechamento=payload.id_modelo,
        n_dezenas_base=modelo.n_dezenas,
        score_medio=float(sum(item["score"] for item in resultados) / len(resultados)) if resultados else None,
        data_geracao=timestamp,
    )
    salvar_aposta(aposta)

    return {
        "modelo": modelo_dict,
        "total_jogos_modelo": len(jogos),
        "total_jogos_retorno": len(resultados),
        "custo_total": modelo.preco_total,
        "resultados": resultados,
        "disclaimer": "Ferramenta para análise/entretenimento. Não há garantia de prêmios.",
    }
