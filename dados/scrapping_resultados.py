"""
Pipeline de ingestão do histórico oficial de concursos da Lotofácil.
"""

from __future__ import annotations

import json
import ssl
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd

URL = (
    "https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/"
    "download?modalidade=Lotof%C3%A1cil"
)
DESTINO_PADRAO = Path("./base/resultados.csv")
DESTINO_LONG = Path("./base/concursos_long.csv")
DESTINO_STATS = Path("./base/estatisticas_concursos.json")
DESTINO_META = Path("./base/meta_atualizacao.json")


def xls_resultados(url: str = URL) -> pd.DataFrame:
    """Obtém a planilha oficial (XLS) com todos os sorteios."""

    ssl._create_default_https_context = ssl._create_unverified_context
    return pd.read_excel(url)


def preparar_resultados(dados: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicidades e padroniza o nome das colunas."""

    base = dados.drop_duplicates("Concurso").copy()
    colunas = {
        "Bola1": "B1",
        "Bola2": "B2",
        "Bola3": "B3",
        "Bola4": "B4",
        "Bola5": "B5",
        "Bola6": "B6",
        "Bola7": "B7",
        "Bola8": "B8",
        "Bola9": "B9",
        "Bola10": "B10",
        "Bola11": "B11",
        "Bola12": "B12",
        "Bola13": "B13",
        "Bola14": "B14",
        "Bola15": "B15",
    }

    col_ganhadores_variantes = [
        "Ganhadores_15_Números",
        "Ganhadores_15_N\u00fameros",
        "Ganhadores_15_Nǧmeros",
    ]
    for coluna in col_ganhadores_variantes:
        if coluna in base.columns:
            colunas[coluna] = "Ganhou"
            break

    base.rename(columns=colunas, inplace=True)
    return base


def ler_existente(destino: Path) -> Optional[pd.DataFrame]:
    """Retorna o CSV já salvo, se existir."""

    if destino.exists():
        return pd.read_csv(destino, sep=";", encoding="utf8")
    return None


def combinar_datasets(
    novo: pd.DataFrame,
    existente: Optional[pd.DataFrame],
) -> Tuple[pd.DataFrame, int]:
    """Concatena datasets e retorna o total de concursos novos."""

    if existente is None:
        combinado = novo
        novos = len(novo)
    else:
        combinado = pd.concat([existente, novo], ignore_index=True)
        combinado = combinado.drop_duplicates("Concurso").sort_values("Concurso")
        novos = len(combinado) - len(existente)
    return combinado, max(novos, 0)


def salvar_resultados(dados: pd.DataFrame, destino: Path = DESTINO_PADRAO) -> Path:
    """Exporta os dados limpos para CSV."""

    destino.parent.mkdir(parents=True, exist_ok=True)
    dados.to_csv(destino, sep=";", encoding="utf8", index=False)
    return destino


def gerar_concursos_long(
    dados: pd.DataFrame,
    destino: Path = DESTINO_LONG,
) -> Path:
    """Cria a visão long (uma linha por dezena/concurso)."""

    dezenas_cols = [col for col in dados.columns if col.startswith("B")]
    long_df = dados.melt(
        id_vars=["Concurso", "Data Sorteio"],
        value_vars=dezenas_cols,
        var_name="Posicao",
        value_name="Dezena",
    )
    long_df["Sorteada"] = 1

    destino.parent.mkdir(parents=True, exist_ok=True)
    long_df.to_csv(destino, sep=";", encoding="utf8", index=False)
    return destino


def calcular_estatisticas(dados: pd.DataFrame) -> Dict[str, object]:
    """Gera estatísticas básicas para alimentar dashboards/IA."""

    dezenas_cols = [col for col in dados.columns if col.startswith("B")]
    freq = dados[dezenas_cols].melt(value_name="Dezena")["Dezena"].value_counts()
    freq_dict = {int(k): int(v) for k, v in freq.sort_index().items()}

    resumo = obter_resumo_ultimo_concurso(dados)
    return {
        "total_concursos": int(len(dados)),
        "frequencia_dezenas": freq_dict,
        "ultimo_concurso": resumo.get("concurso"),
        "ultima_data": resumo.get("data"),
        "gerado_em": datetime.utcnow().isoformat() + "Z",
    }


def salvar_estatisticas(
    estatisticas: Dict[str, object],
    destino: Path = DESTINO_STATS,
) -> Path:
    """Grava as estatísticas em JSON."""

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(estatisticas, ensure_ascii=False, indent=2),
        encoding="utf8",
    )
    return destino


def salvar_meta(meta: Dict[str, object], destino: Path = DESTINO_META) -> Path:
    """Registra informações da última atualização."""

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf8",
    )
    return destino


def atualizar_resultados(
    url: str = URL,
    destino: Path = DESTINO_PADRAO,
    gerar_visoes: bool = True,
) -> Dict[str, object]:
    """
    Executa o fluxo completo (download → limpeza → persistência + visões).
    """

    dados = preparar_resultados(xls_resultados(url))
    existente = ler_existente(destino)
    combinado, novos = combinar_datasets(dados, existente)
    salvar_resultados(combinado, destino)

    estatisticas = calcular_estatisticas(combinado)
    if gerar_visoes:
        gerar_concursos_long(combinado, DESTINO_LONG)
        salvar_estatisticas(estatisticas, DESTINO_STATS)

    meta = {
        "ultimo_concurso": estatisticas["ultimo_concurso"],
        "ultima_data": estatisticas["ultima_data"],
        "total_concursos": estatisticas["total_concursos"],
        "novos_registros": novos,
        "atualizado_em": estatisticas["gerado_em"],
    }
    salvar_meta(meta, DESTINO_META)
    return {"meta": meta, "estatisticas": estatisticas, "csv": str(destino)}


def obter_resumo_ultimo_concurso(dados: pd.DataFrame) -> Dict[str, Optional[str]]:
    """Retorna data e número do último concurso."""

    concurso = int(dados["Concurso"].max())
    linha = dados[dados["Concurso"] == concurso]
    data_sorteio = linha["Data Sorteio"].iloc[0] if not linha.empty else None
    return {"concurso": concurso, "data": data_sorteio}


def main() -> None:
    """Função utilitária que roda o ETL completo."""

    resultado = atualizar_resultados()
    meta = resultado["meta"]

    print("\n\033[1;32mRESULTADOS ATUALIZADOS COM SUCESSO!\033[m")
    print(
        f"\n\033[1;36mÚltimo sorteio:\033[m {meta['ultima_data']}"
        f"\n\033[1;36mConcurso:\033[m {meta['ultimo_concurso']}"
    )
    print(f"\n\033[1;33mNovos registros nesta execução:\033[m {meta['novos_registros']}")
    print(f"\n\033[1;35mArquivo salvo em:\033[m \033[1;33m{resultado['csv']}\033[m")


if __name__ == "__main__":
    main()
