import sys
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.features import calcular_estatisticas_avancadas  # noqa: E402
from app.fechamentos import aplicar_fechamento, listar_modelos  # noqa: E402
from app.ia import score_jogos, sugerir_dezenas, sugerir_estrategias  # noqa: E402
from app.ia.universo import gerar_universo_neural, registrar_teste_fechamento  # noqa: E402
from app.simulacoes import simular_ultimos  # noqa: E402

st.set_page_config(page_title="Lotofácil IA – Painel", layout="wide")
st.title("Lotofácil IA – Painel de Análise e Entretenimento")
st.caption("Ferramenta experimental para entretenimento. Nenhuma sugestão garante prêmios.")


@st.cache_data(ttl=3600)
def carregar_estatisticas():
    return calcular_estatisticas_avancadas()


@st.cache_data(ttl=3600)
def carregar_modelos_cached():
    return listar_modelos()


def modelos_dataframe():
    modelos = carregar_modelos_cached()
    data = []
    for modelo in modelos:
        data.append(
            {
                "Modelo": modelo.id_modelo,
                "Descrição": modelo.descricao,
                "Garantia": modelo.tipo_garantia,
                "Universo": modelo.n_dezenas,
                "Jogos": modelo.n_jogos,
                "Valor Total (R$)": modelo.preco_total,
            }
        )
    df = pd.DataFrame(data)
    return df.sort_values(["Universo", "Garantia"]), {m.id_modelo: m for m in modelos}


def render_estatisticas_tab():
    stats = carregar_estatisticas()
    dezenas_df = (
        pd.DataFrame(stats["dezenas"])
        .T.reset_index()
        .rename(columns={"index": "dezena"})
        .astype({"dezena": int})
        .sort_values("freq_50", ascending=False)
    )
    st.subheader("Frequência e atrasos por dezena")
    st.dataframe(dezenas_df, height=400, width="stretch")
    st.bar_chart(dezenas_df.set_index("dezena")["freq_50"])

    st.subheader("Distribuições históricas")
    col1, col2 = st.columns(2)
    dist_pares = pd.DataFrame(stats["distribuicoes"]["pares_impares"])
    dist_moldura = pd.DataFrame(stats["distribuicoes"]["moldura_miolo"])
    with col1:
        st.write("Pares x Ímpares")
        st.dataframe(dist_pares, width="stretch")
    with col2:
        st.write("Moldura x Miolo")
        st.dataframe(dist_moldura, width="stretch")


def render_ia_tab():
    st.subheader("Sugestão de dezenas com IA")
    col1, col2, col3 = st.columns(3)
    n_dezenas = col1.slider("Quantidade de dezenas", 15, 21, 17)
    modo = col2.selectbox("Modo", ["mix", "probabilidade", "atraso"])
    usar_modelo = col3.checkbox("Tentar usar modelo treinado", True)
    if st.button("Gerar sugestão"):
        sugestao = sugerir_dezenas(n_dezenas=n_dezenas, modo=modo, usar_modelo=usar_modelo)
        st.success(f"Dezenas sugeridas ({sugestao['modo']}):")
        st.write(" ".join(map(lambda x: str(x).zfill(2), sugestao["dezenas"])))

    st.divider()
    st.subheader("Recomendação de estratégias (universo + modelo)")
    col_budget, col_profile, col_limit = st.columns(3)
    orcamento = col_budget.number_input("Orçamento máximo (R$)", min_value=3.0, value=150.0, step=3.0)
    perfil = col_profile.selectbox(
        "Perfil",
        [
            ("conservador", "Conservador"),
            ("balanceado", "Balanceado"),
            ("agressivo", "Agressivo"),
        ],
        format_func=lambda item: item[1],
    )[0]
    limite = col_limit.slider("Limitar resultados", 1, 10, 5)
    if st.button("Sugerir estratégias", key="estrategia"):
        estrategias = sugerir_estrategias(orçamento=orcamento, perfil=perfil, limite=limite)
        if estrategias.empty:
            st.warning("Nenhuma estratégia encontrada dentro do orçamento definido.")
        else:
            st.dataframe(estrategias, width="stretch")


def render_fechamentos_tab():
    st.subheader("Aplicar fechamento manualmente")
    df_modelos, modelos_map = modelos_dataframe()
    st.dataframe(df_modelos, height=300, width="stretch")
    modelo_id = st.selectbox("Escolha o modelo", df_modelos["Modelo"])
    modelo = modelos_map[modelo_id]
    dezenas_default = list(range(1, modelo.n_dezenas + 1))
    dezenas_input = st.text_input(
        f"Informe {modelo.n_dezenas} dezenas separadas por espaço",
        " ".join(str(n).zfill(2) for n in dezenas_default),
    )
    ordenar = st.checkbox("Ordenar por score", True)
    limitar = st.number_input("Manter os primeiros N jogos (opcional)", min_value=0, value=0)

    if st.button("Gerar jogos", key="manual"):
        try:
            dezenas = [int(x) for x in dezenas_input.split()]
            jogos = aplicar_fechamento(dezenas, modelo.id_modelo)
            resultados = score_jogos(jogos)
            if ordenar:
                resultados = sorted(resultados, key=lambda item: item["score"], reverse=True)
            if limitar:
                resultados = resultados[: int(limitar)]
            df = pd.DataFrame(resultados)
            st.dataframe(df, width="stretch")
            csv = df.to_csv(index=False).encode("utf8")
            st.download_button("Baixar CSV", csv, file_name="fechamento.csv", mime="text/csv")
        except ValueError as exc:
            st.error(str(exc))


def _parse_jogos_text(texto: str) -> List[List[int]]:
    jogos = []
    for linha in texto.strip().splitlines():
        linha = linha.strip()
        if not linha:
            continue
        numeros = [int(x) for x in linha.replace(",", " ").split()]
        if len(numeros) != 15:
            raise ValueError("Cada linha deve conter exatamente 15 dezenas.")
        jogos.append(sorted(numeros))
    return jogos


def render_simulacao_tab():
    st.subheader("Simular estratégia nos últimos concursos")
    jogos_texto = st.text_area(
        "Informe um jogo por linha (15 dezenas). Exemplo: 01 02 03 ... 15",
        height=150,
    )
    ultimos = st.slider("Quantidade de concursos para backtest", 50, 2000, 200, step=50)
    registrar = st.checkbox("Registrar resultados em auditoria", value=False)

    if st.button("Simular estratégia"):
        try:
            jogos = _parse_jogos_text(jogos_texto)
            resultado = simular_ultimos(jogos, ultimos=ultimos, registrar=registrar)
            st.write(f"Concursos analisados: {resultado['total_concursos']}")
            st.write(f"Prêmio estimado total: R$ {resultado['premio_estimado_total']:.2f}")
            st.json(resultado["distribuicao_acertos"])
            resultados_df = pd.DataFrame(resultado["resultados"])
            if not resultados_df.empty:
                st.dataframe(resultados_df, width="stretch")
        except ValueError as exc:
            st.error(str(exc))


def mostrar_historico_testes():
    caminho = Path("./base/testes_fechamentos.csv")
    if caminho.exists():
        df = pd.read_csv(caminho)
        st.subheader("Histórico recente de testes (últimos 10)")
        st.dataframe(df.tail(10), width="stretch")


def render_fechamento_ia_tab():
    st.subheader("Fechamento com IA (treinamento transparente)")
    df_modelos, modelos_map = modelos_dataframe()
    st.dataframe(df_modelos, height=300, width="stretch")
    modelo_id = st.selectbox("Selecione o modelo", df_modelos["Modelo"], key="modelo_ia")
    modelo = modelos_map[modelo_id]

    col1, col2, col3 = st.columns(3)
    acuracia_desejada = col1.slider("Acurácia desejada (%)", 85.0, 99.0, 98.0, step=0.1)
    probabilidade_min = col2.slider("Probabilidade mínima (%)", 90.0, 99.9, 99.0, step=0.1)
    max_retreinos = col3.number_input("Limite de treinos (max_retreinos)", min_value=1, value=20, step=1)
    top_jogos = st.number_input("Manter top N jogos após score", min_value=10, value=100)

    status_box = st.empty()

    def atualizar_status(msg: str):
        status_box.info(msg)

    if st.button("Executar fluxo completo com IA"):
        try:
            universo = gerar_universo_neural(
                n_dezenas=modelo.n_dezenas,
                acuracia_min=acuracia_desejada / 100,
                probabilidade_min=probabilidade_min,
                max_retreinos=int(max_retreinos),
                progresso=atualizar_status,
            )
        except RuntimeError as exc:
            st.error(str(exc))
            return

        st.success(
            f"Universo encontrado! Acurácia atingida: {universo.pontuacao_modelo*100:.2f}% "
            f"(alvo {acuracia_desejada:.2f}%)."
        )
        if universo.pontuacao_modelo * 100 < acuracia_desejada:
            st.warning(
                "O modelo atual não alcançou a acurácia solicitada. "
                "Os números abaixo correspondem ao melhor resultado disponível."
            )
        st.write(f"Probabilidade do jogo base: {universo.probabilidade_jogo:.2f}%")
        st.code(" ".join(str(d).zfill(2) for d in universo.dezenas), language="text")

        jogos = aplicar_fechamento(universo.dezenas, modelo.id_modelo)
        resultados = score_jogos(jogos)
        resultados = sorted(resultados, key=lambda item: item["score"], reverse=True)[: int(top_jogos)]
        df = pd.DataFrame(resultados)
        st.dataframe(df, width="stretch")
        csv = df.to_csv(index=False).encode("utf8")
        st.download_button("Baixar jogos testados (CSV)", csv, file_name="fechamento_ia.csv", mime="text/csv")

        registrar_teste_fechamento(
            id_modelo=modelo.id_modelo,
            universo=universo,
            garantia=modelo.tipo_garantia,
            total_jogos=len(df),
        )
        st.caption("Resultado registrado em `base/testes_fechamentos.csv`.")
        mostrar_historico_testes()


tabs = st.tabs(
    [
        "Estatísticas",
        "IA / Sugestões",
        "Fechamentos",
        "Fechamento com IA",
        "Simulações",
    ]
)

with tabs[0]:
    render_estatisticas_tab()
with tabs[1]:
    render_ia_tab()
with tabs[2]:
    render_fechamentos_tab()
with tabs[3]:
    render_fechamento_ia_tab()
with tabs[4]:
    render_simulacao_tab()
