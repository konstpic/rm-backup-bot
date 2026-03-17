import asyncio
from pathlib import Path
from typing import Callable, Awaitable

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from .backup import create_backup_pair
from .config import Settings


BackupFunc = Callable[[Settings], Awaitable[tuple[Path, Path]]]


async def _run_backup(settings: Settings) -> tuple[Path, Path]:
    loop = asyncio.get_running_loop()
    # Вынести блокирующий бэкап в отдельный поток
    return await loop.run_in_executor(None, create_backup_pair, settings)


def create_dispatcher(settings: Settings) -> Dispatcher:
    dp = Dispatcher()

    @dp.message(Command("start", "help"))
    async def cmd_start(message: Message) -> None:
        if str(message.chat.id) != settings.telegram_chat_id:
            # Игнорируем чужие чаты, чтобы не светить наличие бота
            return
        await message.answer("Бот бэкапов готов. Команда /backup создаст дамп и Excel и пришлёт их сюда.")

    @dp.message(Command("backup"))
    async def cmd_backup(message: Message) -> None:
        if str(message.chat.id) != settings.telegram_chat_id:
            # Молча игнорируем команды из других чатов
            return
        await message.answer("Делаю бэкап, подождите...")
        try:
            sql_path, excel_path = await _run_backup(settings)
        except Exception as exc:  # noqa: BLE001
            await message.answer(f"Ошибка при создании бэкапа: {exc}")
            return

        try:
            await message.answer_document(
                document=sql_path.open("rb"),
                caption="SQL-дамп базы",
            )
            await message.answer_document(
                document=excel_path.open("rb"),
                caption="Excel-отчёт по данным",
            )
        finally:
            # Удаляем временные файлы
            for path in (sql_path, excel_path):
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    pass

    return dp


async def send_scheduled_backup(bot: Bot, settings: Settings) -> None:
    """
    Используется планировщиком: создаёт бэкап и шлёт файлы в TELEGRAM_CHAT_ID.
    """
    try:
        sql_path, excel_path = await _run_backup(settings)
    except Exception as exc:  # noqa: BLE001
        # Отправляем сообщение об ошибке в основной чат
        await bot.send_message(chat_id=settings.telegram_chat_id, text=f"Ошибка планового бэкапа: {exc}")
        return

    try:
        await bot.send_document(
            chat_id=settings.telegram_chat_id,
            document=sql_path.open("rb"),
            caption="Плановый SQL-дамп базы",
        )
        await bot.send_document(
            chat_id=settings.telegram_chat_id,
            document=excel_path.open("rb"),
            caption="Плановый Excel-отчёт по данным",
        )
    finally:
        for path in (sql_path, excel_path):
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass


