# Frontend Streamlit – Lotofácil IA

O projeto já inclui um painel interativo simples baseado em [Streamlit](https://streamlit.io) que permite consumir as principais funcionalidades do backend diretamente em Python.

## Como executar

1. Garanta que as dependências estejam instaladas (incluindo `streamlit`):

   ```bash
   pip install -r requirements.txt
   ```

2. No diretório raiz do repositório, execute:

   ```bash
    streamlit run frontend/streamlit_app.py
   ```

3. O Streamlit abrirá automaticamente em `http://localhost:8501`.

## Funcionalidades disponíveis

- **Estatísticas**: visualiza frequências, atrasos e distribuições pares/ímpares e moldura/miolo calculadas a partir dos dados históricos.
- **IA / Sugestões**:
  - Sugestão de dezenas usando heurísticas ou (quando treinado) o modelo por dezena.
  - Recomendação de estratégias (N + modelo de fechamento) com base no orçamento e perfil.
- **Fechamentos**:
  - Seleciona um modelo do catálogo, aplica a matriz e lista os jogos com `score_jogos`. Permite download em CSV.
- **Simulações**:
  - Permite informar jogos (15 dezenas por linha) e executar backtests nos últimos N concursos. Há opção de registrar os resultados em auditoria.

> **Aviso**: todas as análises são para fins de entretenimento. Não há garantia de ganhos reais nas loterias.
