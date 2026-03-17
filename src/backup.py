import datetime as dt
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple

import pandas as pd

from .config import Settings
from . import db


def create_sql_dump(settings: Settings) -> Path:
    """
    Создаёт SQL-дамп через pg_dump и возвращает путь к файлу.
    Формат plain SQL, пригодный для psql/pg_restore.
    """
    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    tmp_dir = Path(tempfile.gettempdir())
    dump_path = tmp_dir / f"remnawave-backup-{timestamp}.sql"

    env = os.environ.copy()
    env["PGPASSWORD"] = settings.db_password

    cmd = [
        "pg_dump",
        "-h",
        settings.db_host,
        "-p",
        str(settings.db_port),
        "-U",
        settings.db_user,
        "-d",
        settings.db_name,
        "-F",
        "p",
    ]

    with dump_path.open("wb") as f:
        subprocess.run(cmd, check=True, stdout=f, env=env)

    return dump_path


def create_excel_report(settings: Settings) -> Path:
    """
    Формирует Excel-файл: по листу на каждую таблицу из схемы public
    (или список из EXCEL_TABLES).
    """
    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    tmp_dir = Path(tempfile.gettempdir())
    excel_path = tmp_dir / f"remnawave-report-{timestamp}.xlsx"

    tables = db.fetch_tables(settings)

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for table in tables:
            try:
                data = db.fetch_table_data(settings, table)
                if not data:
                    # Пустая таблица — создаём пустой DataFrame
                    df = pd.DataFrame()
                else:
                    df = pd.DataFrame(data)
                sheet_name = table[:31]  # Ограничение Excel на длину имени листа
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            except Exception:
                # Не прерываем генерацию всего файла из-за одной проблемной таблицы
                continue

    return excel_path


def create_backup_pair(settings: Settings) -> Tuple[Path, Path]:
    """
    Создаёт SQL-дамп и Excel-отчёт и возвращает пути к двум файлам.
    """
    sql_path = create_sql_dump(settings)
    excel_path = create_excel_report(settings)
    return sql_path, excel_path


