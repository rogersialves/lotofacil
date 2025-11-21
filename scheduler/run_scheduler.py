"""Scheduler simples para atualização de dados e re-treino periódico."""

import os
from apscheduler.schedulers.blocking import BlockingScheduler

from dados import scrapping_resultados
from app.ml.pipelines import treinar_modelo_dezena, treinar_modelo_jogo
from app.core.logging import log_entretenimento


def atualizar_dados():
    scrapping_resultados.atualizar_resultados()
    log_entretenimento("Scheduler: atualização de dados concluída")


def treinar_modelos():
    treinar_modelo_dezena()
    treinar_modelo_jogo()
    log_entretenimento("Scheduler: re-treino de modelos concluído")


def main():
    if os.getenv("RUN_ONCE") == "1":
        atualizar_dados()
        treinar_modelos()
        return

    scheduler = BlockingScheduler()
    scheduler.add_job(atualizar_dados, "cron", hour=3, minute=0)
    scheduler.add_job(treinar_modelos, "cron", day_of_week="sun", hour=4, minute=0)
    log_entretenimento("Scheduler iniciado")
    scheduler.start()


if __name__ == "__main__":
    main()
