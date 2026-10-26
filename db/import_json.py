"""Однократный перенос данных проекта из JSON-файлов в базу SQLite.

Порядок импорта важен: сначала таблицы, на которые ссылаются внешние
ключи (категории, пользователи), затем интересы, подписки и занятия.
Запуск из корня проекта: python -m db.import_json
"""
import json

from db.database import BASE_DIR, get_connection

DATA_DIR = BASE_DIR / "data"
CATEGORIES_FILE = DATA_DIR / "categories.json"
USERS_FILE = DATA_DIR / "users.json"
INTERESTS_FILE = DATA_DIR / "interests.json"
SUBSCRIPTIONS_FILE = DATA_DIR / "subscriptions.json"


def load_json(filename):
    """Прочитать список записей из JSON-файла."""
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def import_categories(conn):
    """Перенести категории в таблицу categories."""
    categories = load_json(CATEGORIES_FILE)
    conn.executemany(
        """
        INSERT INTO categories (
            id,
            name
        )
        VALUES (?, ?)
        """,
        [
            (
                category["id"],
                category["name"],
            )
            for category in categories
        ],
    )


def import_users(conn):
    """Перенести пользователей в таблицу users."""
    users = load_json(USERS_FILE)
    conn.executemany(
        """
        INSERT INTO users (
            id,
            name,
            email
        )
        VALUES (?, ?, ?)
        """,
        [
            (
                user["id"],
                user["name"],
                user["email"],
            )
            for user in users
        ],
    )


def import_interests(conn):
    """Перенести интересы в таблицу interests."""
    interests = load_json(INTERESTS_FILE)
    conn.executemany(
        """
        INSERT INTO interests (
            id,
            name,
            category_id,
            weekly_goal,
            is_active
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                interest["id"],
                interest["name"],
                interest["category_id"],
                interest["weekly_goal"],
                int(interest["is_active"]),
            )
            for interest in interests
        ],
    )


def import_subscriptions(conn):
    """Перенести подписки в таблицу subscriptions."""
    subscriptions = load_json(SUBSCRIPTIONS_FILE)
    conn.executemany(
        """
        INSERT INTO subscriptions (
            id,
            user_id,
            interest_id,
            start_date,
            is_cancelled
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                subscription["id"],
                subscription["user_id"],
                subscription["interest_id"],
                subscription["start_date"],
                int(subscription["is_cancelled"]),
            )
            for subscription in subscriptions
        ],
    )


def import_activities(conn):
    """Перенести занятия: словарь hours_by_date подписки -> строки таблицы.

    Каждая пара «дата: часы» из подписки становится отдельной записью
    таблицы activities со ссылкой на подписку.
    """
    subscriptions = load_json(SUBSCRIPTIONS_FILE)
    activities = []
    for subscription in subscriptions:
        for day, hours in subscription["hours_by_date"].items():
            activities.append((subscription["id"], day, hours))
    conn.executemany(
        """
        INSERT INTO activities (
            subscription_id,
            activity_date,
            hours
        )
        VALUES (?, ?, ?)
        """,
        activities,
    )


def main():
    """Выполнить импорт в одной транзакции: при ошибке откатить всё."""
    conn = get_connection()
    try:
        import_categories(conn)
        import_users(conn)
        import_interests(conn)
        import_subscriptions(conn)
        import_activities(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
