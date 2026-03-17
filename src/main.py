import asyncio

from aiogram import Bot

from .config import load_settings
from .scheduler import setup_scheduler
from .telegram_bot import create_dispatcher


async def main() -> None:
    settings = load_settings()
    bot = Bot(token=settings.telegram_bot_token)
    dp = create_dispatcher(settings)

    scheduler = setup_scheduler(bot, settings)
    try:
        await dp.start_polling(bot)
    finally:
        if scheduler:
            scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())

