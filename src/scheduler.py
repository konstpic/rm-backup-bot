from __future__ import annotations

from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from aiogram import Bot

from .config import Settings
from .telegram_bot import send_scheduled_backup


def setup_scheduler(bot: Bot, settings: Settings) -> Optional[AsyncIOScheduler]:
    """
    Настраивает планировщик, если задан BACKUP_SCHEDULE_CRON.
    Возвращает инстанс планировщика или None, если расписание не задано.
    """
    if not settings.backup_schedule_cron:
        return None

    trigger = CronTrigger.from_crontab(settings.backup_schedule_cron)
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(send_scheduled_backup, trigger=trigger, args=[bot, settings])
    scheduler.start()
    return scheduler


