"""Просмотр структуры исходной базы ПР7 перед переносом данных в ORM.

Скрипт только читает базу: выводит таблицы, столбцы, число записей
и проверяет, что внешние ключи указывают на существующие записи.
Запуск из корня проекта: python db/inspect_source_db.py
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / "data" / "interest_tracker.sqlite"

if not SOURCE_DB.exists():
    raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

with sqlite3.connect(SOURCE_DB) as connection:
    connection.row_factory = sqlite3.Row
    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    for (table_name,) in tables:
        print(f"\nТаблица: {table_name}")
        columns = connection.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()
        print("Столбцы:")
        for column in columns:
            print(
                f"  имя={column['name']}, "
                f"тип={column['type']}, "
                f"NOT NULL={column['notnull']}, "
                f"PRIMARY KEY={column['pk']}"
            )
        count = connection.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        ).fetchone()[0]
        print(f"Количество записей: {count}")
    broken = connection.execute("PRAGMA foreign_key_check").fetchall()
    print(f"\nНарушений внешних ключей: {len(broken)}")
