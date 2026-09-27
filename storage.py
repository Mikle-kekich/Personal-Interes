"""Загрузка и сохранение объектов проекта в JSON-файлах.

В файлах хранятся списки словарей, даты записаны строками ГГГГ-ММ-ДД.
Связанные объекты записываются номерами: category_id, user_id,
interest_id. При загрузке по номерам находятся нужные объекты.
"""
import json
from pathlib import Path
from typing import List

from models import Category, Interest, Subscription, User
from models.categories import find_category_by_id
from models.interests import find_interest_by_id
from models.users import find_user_by_id


def _read_json(filename: Path) -> List[dict]:
    """Прочитать список записей из JSON-файла.

    Если файла нет или он повреждён, вернуть пустой список.
    """
    try:
        with open(filename, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Файл {filename} повреждён, данные из него не загружены.")
        return []


def _write_json(filename: Path, records: List[dict]) -> None:
    """Записать список записей в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)


def load_categories(filename: Path) -> List[Category]:
    """Загрузить категории из JSON-файла и создать объекты Category."""
    categories = []
    for data in _read_json(filename):
        categories.append(Category(data["id"], data["name"]))
    return categories


def save_categories(filename: Path, categories: List[Category]) -> None:
    """Сохранить объекты Category в JSON-файл."""
    records = []
    for category in categories:
        records.append({"id": category.id, "name": category.name})
    _write_json(filename, records)


def load_interests(
    filename: Path, categories: List[Category]
) -> List[Interest]:
    """Загрузить интересы и связать каждый с объектом Category.

    Интерес с несуществующей категорией не загружается.
    """
    interests = []
    for data in _read_json(filename):
        category = find_category_by_id(categories, data["category_id"])
        if category is None:
            print(f"Интерес {data['id']} пропущен: нет категории.")
            continue
        interest = Interest(
            data["id"], data["name"], category, data["weekly_goal"]
        )
        interest.is_active = data["is_active"]
        interests.append(interest)
    return interests


def save_interests(filename: Path, interests: List[Interest]) -> None:
    """Сохранить объекты Interest; вместо категории записать её номер."""
    records = []
    for interest in interests:
        records.append({
            "id": interest.id,
            "name": interest.name,
            "category_id": interest.category.id,
            "weekly_goal": interest.weekly_goal,
            "is_active": interest.is_active,
        })
    _write_json(filename, records)


def load_users(filename: Path) -> List[User]:
    """Загрузить пользователей с помощью метода класса User.from_data()."""
    users = []
    for data in _read_json(filename):
        users.append(User.from_data(data))
    return users


def save_users(filename: Path, users: List[User]) -> None:
    """Сохранить объекты User в JSON-файл."""
    records = []
    for user in users:
        records.append({"id": user.id, "name": user.name, "email": user.email})
    _write_json(filename, records)


def load_subscriptions(
    filename: Path, users: List[User], interests: List[Interest]
) -> List[Subscription]:
    """Загрузить подписки и связать их с объектами User и Interest.

    Подписка, у которой не найден пользователь или интерес,
    не загружается.
    """
    subscriptions = []
    for data in _read_json(filename):
        user = find_user_by_id(users, data["user_id"])
        interest = find_interest_by_id(interests, data["interest_id"])
        if user is None or interest is None:
            print(
                f"Подписка {data['id']} пропущена: "
                "нет пользователя или интереса."
            )
            continue
        subscription = Subscription(
            data["id"], user, interest, data["start_date"]
        )
        subscription.is_cancelled = data["is_cancelled"]
        subscription.hours_by_date = data["hours_by_date"]
        subscriptions.append(subscription)
    return subscriptions


def save_subscriptions(
    filename: Path, subscriptions: List[Subscription]
) -> None:
    """Сохранить объекты Subscription; вместо объектов записать номера."""
    records = []
    for subscription in subscriptions:
        records.append({
            "id": subscription.id,
            "user_id": subscription.user.id,
            "interest_id": subscription.interest.id,
            "start_date": subscription.start_date,
            "is_cancelled": subscription.is_cancelled,
            "hours_by_date": subscription.hours_by_date,
        })
    _write_json(filename, records)
