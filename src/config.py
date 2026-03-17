import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Settings:
    telegram_bot_token: str
    telegram_chat_id: str

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    backup_schedule_cron: Optional[str]
    excel_tables: Optional[List[str]]


def _get_env(name: str, required: bool = True, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_settings() -> Settings:
    excel_tables_raw = os.getenv("EXCEL_TABLES")
    excel_tables: Optional[List[str]] = None
    if excel_tables_raw:
        excel_tables = [t.strip() for t in excel_tables_raw.split(",") if t.strip()]

    schedule = os.getenv("BACKUP_SCHEDULE_CRON") or None

    return Settings(
        telegram_bot_token=_get_env("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=_get_env("TELEGRAM_CHAT_ID"),
        db_host=_get_env("DB_HOST", default="remnawave-db"),
        db_port=int(_get_env("DB_PORT", required=False, default="5432")),
        db_name=_get_env("DB_NAME"),
        db_user=_get_env("DB_USER"),
        db_password=_get_env("DB_PASSWORD"),
        backup_schedule_cron=schedule,
        excel_tables=excel_tables,
    )

