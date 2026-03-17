import asyncio
import logging

from aiogram import Bot

from .config import load_settings
from .scheduler import setup_scheduler
from .telegram_bot import create_dispatcher


async def main() -> None:
    # Базовая настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger("rm-backup-bot")

    settings = load_settings()

    # Логируем конфиг без чувствительных данных
    logger.info(
        "Starting backup bot with config: chat_id=%s, db_host=%s, db_port=%s, db_name=%s, db_user=%s, "
        "schedule=%s, excel_tables=%s",
        settings.telegram_chat_id,
        settings.db_host,
        settings.db_port,
        settings.db_name,
        settings.db_user,
        settings.backup_schedule_cron or "<disabled>",
        ",".join(settings.excel_tables) if settings.excel_tables else "<all public tables>",
    )

    bot = Bot(token=settings.telegram_bot_token)
    dp = create_dispatcher(settings)

    scheduler = setup_scheduler(bot, settings)
    if scheduler:
        jobs = scheduler.get_jobs()
        if jobs:
            logger.info("Next scheduled backup at (UTC): %s", jobs[0].next_run_time)
        else:
            logger.info("Scheduler started but no jobs registered.")
    else:
        logger.info("Scheduler is disabled (no BACKUP_SCHEDULE_CRON).")

    try:
        logger.info("Bot polling started.")
        await dp.start_polling(bot)
    finally:
        if scheduler:
            logger.info("Shutting down scheduler...")
            scheduler.shutdown(wait=False)
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())

