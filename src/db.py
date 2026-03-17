from contextlib import contextmanager
from typing import Iterator

import psycopg2
import psycopg2.extras

from .config import Settings


@contextmanager
def get_connection(settings: Settings) -> Iterator[psycopg2.extensions.connection]:
    conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )
    try:
        yield conn
    finally:
        conn.close()


def fetch_tables(settings: Settings) -> list[str]:
    """
    Возвращает список таблиц схемы public, отфильтрованный по excel_tables, если задан.
    """
    if settings.excel_tables:
        return settings.excel_tables

    with get_connection(settings) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            )
            rows = cur.fetchall()
    return [row["table_name"] for row in rows]


def fetch_table_data(settings: Settings, table_name: str) -> list[dict]:
    with get_connection(settings) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f'SELECT * FROM public."{table_name}"')
            rows = cur.fetchall()
    return [dict(row) for row in rows]


