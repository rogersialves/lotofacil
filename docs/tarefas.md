# Plano de Tarefas – Plataforma Lotofácil IA

Legenda de status:

- `[ ]` Pendente
- `[~]` Em andamento
- `[x]` Concluído

## Trilha 1 – Dados & ETL

1. `[x]` Normalizar pipeline de ingestão (scraping oficial → CSV → tabelas `concursos`/`concursos_long`) reutilizando `dados/scrapping_resultados.py`.
2. `[x]` Implementar verificação incremental (somente concursos novos) e registro em `meta_atualizacao`.
3. `[x]` Gerar visões derivadas (`concursos_long`, estatísticas agregadas) para alimentar features.

## Trilha 2 – Estatísticas & Features

1. `[x]` Calcular métricas rolling (freq_10/freq_20/freq_50, atraso, pares/ímpares, moldura) a partir da base normalizada.
2. `[x]` Produzir datasets `Dataset_dezena`, `Dataset_jogo`, `Dataset_estrategias_fechamento` com versionamento.
3. `[x]` Disponibilizar pacote `app/features` com funções reutilizáveis nos serviços/API.

## Trilha 3 – Modelos de IA

1. `[x]` Modelo por dezena (pipeline disponível; treino/local configurado).
2. `[x]` Modelo por jogo (pipeline disponível; treino/local configurado).
3. `[x]` Modelo recomendador de estratégias (`n_dezenas`, `id_modelo_fechamento`) – heurística inicial implementada.
4. `[x]` Registro/MLOps simples (`models/`, tabela `execucoes_modelo`, metadados).

## Trilha 4 – Motor de Fechamentos

1. `[x]` Catalogar `modelos_fechamento` (garantias, nº jogos, custo, observações).
2. `[x]` Persistir matrizes (`matriz_fechamento`) e função `aplicar_fechamento`.
3. `[x]` Integrar com o modelo de jogo para ranquear/filtrar combinações.

## Trilha 5 – API / Backend

1. `[x]` Criar esqueleto FastAPI (`app/api/main.py`) com health check e wiring inicial.
2. `[x]` Implementar endpoints de dados (`/concursos`, `/estatisticas`).
3. `[x]` Expor endpoints de IA (`/ia/sugerir_dezenas`, `/ia/score_jogos`, `/ia/sugerir_n_dezenas`) – heurísticas iniciais disponíveis.
4. `[x]` Endpoints de fechamentos e simulações (`/fechamentos/modelos`, `/fechamentos/gerar`, `/simulacoes`).

## Trilha 6 – Frontend

1. `[x]` MVP Streamlit com painel estatístico + seleção de fechamentos.
2. `[x]` Tela “Fechamento com IA” (orçamento → recomendação → jogos ordenados).
3. `[x]` Exportação/compartilhamento com disclaimers visíveis.

## Trilha 7 – Simulações & Auditoria

1. `[x]` Motor de backtest (`simular_estrategia`, `conferir_apostas`) usando históricos.
2. `[x]` Tabelas `apostas_geradas` e `resultados_apostas` com relatórios.
3. `[x]` Alertas/logs com foco em entretenimento (sem garantia de ganhos).

## Trilha 8 – Infra & Automação

1. `[x]` Containers Docker/Compose orquestrando API + jobs + frontend.
2. `[x]` Scheduler de atualização/retrain (cron/Airflow/Celery beat).
3. `[x]` CI/CD básico rodando lint/testes e validando pipelines de dados.

---

Próximas entregas planejadas: concluir o pipeline de ingestão incremental (Trilha 1) e disponibilizar o backend inicial (Trilha 5) para suportar os demais módulos.
