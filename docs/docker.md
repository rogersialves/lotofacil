# Execução com Docker/Compose

O projeto inclui arquivos de containerização para facilitar a execução local dos serviços principais.

## Pré-requisitos

- Docker ou Docker Desktop instalado.
- Docker Compose v2.

## Como subir os serviços

Na raiz do repositório execute:

```bash
docker compose up --build
```

Serviços expostos:

- `api`: FastAPI disponível em `http://localhost:8000`.
- `streamlit`: painel em `http://localhost:8501`.
- `scheduler`: serviço background que atualiza os dados e agenda re-treinos (cron 03:00 e domingo 04:00).

## Scheduler

O contêiner `scheduler` executa `scheduler/run_scheduler.py`, que usa APScheduler para:

- Baixar/atualizar os concursos diariamente (`scrapping_resultados`).
- Re-treinar os modelos por dezena/jogo semanalmente.

Para testar localmente sem bloquear o terminal:

```bash
RUN_ONCE=1 python scheduler/run_scheduler.py
```

## CI/CD

O workflow GitHub Actions (`.github/workflows/ci.yml`) automatiza:

1. Instalação das dependências.
2. Compilação estática (`python -m compileall`).
3. Execução do scheduler em modo `RUN_ONCE=1`.

> Todos os serviços e relatórios mantêm o aviso de entretenimento. Não há garantias de prêmios.
