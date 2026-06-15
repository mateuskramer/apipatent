import psycopg2
from psycopg2 import extras

from app.core.config import get_settings


def get_db_connection():
    settings = get_settings()
    return psycopg2.connect(
        host=settings.db_host,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_pass,
        port=settings.db_port,
        sslmode=settings.db_sslmode,
    )


def fetch_all(query: str, params: tuple | None = None) -> list[dict]:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]


def fetch_one(query: str, params: tuple | None = None) -> dict | None:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None


def execute_write(query: str, params: tuple | None = None) -> int:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            return cur.rowcount

