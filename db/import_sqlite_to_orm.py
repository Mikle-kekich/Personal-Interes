"""Перенос данных из базы ПР7 (SQLite) в таблицы Django ORM.

Исходная база data/interest_tracker.sqlite только читается, данные
записываются через модели в базу Django (db.sqlite3). Миграции должны
быть применены заранее (python manage.py migrate).

Порядок переноса важен: сначала независимые категории и пользователи,
затем интересы, подписки и занятия, которые ссылаются на них.
Запуск из корня проекта: python db/import_sqlite_to_orm.py
"""
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django
from django.db import transaction

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
SOURCE_DB = BASE_DIR / "data" / "interest_tracker.sqlite"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interest_tracker.settings")
django.setup()

# Модели импортируются только после django.setup().
from interests.models import Category, Interest  # noqa: E402
from subscriptions.models import Activity, Subscription  # noqa: E402
from users.models import User  # noqa: E402


def read_source():
    """Прочитать таблицы исходной базы, не изменяя её.

    Возвращает строки таблиц categories, users, interests,
    subscriptions и activities.
    """
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")
    connection = sqlite3.connect(SOURCE_DB)
    connection.row_factory = sqlite3.Row
    try:
        categories = connection.execute(
            "SELECT id, name FROM categories ORDER BY id"
        ).fetchall()
        users = connection.execute(
            "SELECT id, name, email FROM users ORDER BY id"
        ).fetchall()
        interests = connection.execute(
            """
            SELECT id, name, category_id, weekly_goal, is_active
            FROM interests
            ORDER BY id
            """
        ).fetchall()
        subscriptions = connection.execute(
            """
            SELECT id, user_id, interest_id, start_date, is_cancelled
            FROM subscriptions
            ORDER BY id
            """
        ).fetchall()
        activities = connection.execute(
            """
            SELECT id, subscription_id, activity_date, hours
            FROM activities
            ORDER BY id
            """
        ).fetchall()
    finally:
        connection.close()
    return categories, users, interests, subscriptions, activities


def main():
    """Перенести данные одной транзакцией: при ошибке всё откатывается."""
    categories, users, interests, subscriptions, activities = read_source()
    with transaction.atomic():
        for row in categories:
            Category.objects.update_or_create(
                pk=row["id"],
                defaults={"name": row["name"]},
            )
        for row in users:
            User.objects.update_or_create(
                pk=row["id"],
                defaults={"name": row["name"], "email": row["email"]},
            )
        for row in interests:
            Interest.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "category_id": row["category_id"],
                    "weekly_goal": row["weekly_goal"],
                    "is_active": bool(row["is_active"]),
                },
            )
        for row in subscriptions:
            Subscription.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "user_id": row["user_id"],
                    "interest_id": row["interest_id"],
                    "start_date": date.fromisoformat(row["start_date"]),
                    "is_cancelled": bool(row["is_cancelled"]),
                },
            )
        for row in activities:
            Activity.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "subscription_id": row["subscription_id"],
                    "activity_date": date.fromisoformat(row["activity_date"]),
                    "hours": row["hours"],
                },
            )
    print("Перенос данных завершён.")
    print(f"Категорий: {Category.objects.count()}")
    print(f"Пользователей: {User.objects.count()}")
    print(f"Интересов: {Interest.objects.count()}")
    print(f"Подписок: {Subscription.objects.count()}")
    print(f"Занятий: {Activity.objects.count()}")


if __name__ == "__main__":
    main()
