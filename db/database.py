"""Подключение к базе данных SQLite проекта."""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "interest_tracker.sqlite"


def get_connection() -> sqlite3.Connection:
    """Открыть соединение с базой данных и включить проверку внешних ключей.

    По умолчанию SQLite не проверяет, что внешний ключ указывает на
    существующую запись, поэтому PRAGMA выполняется при каждом подключении.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
