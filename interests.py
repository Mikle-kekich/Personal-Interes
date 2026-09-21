"""Функции для работы с интересами (хобби и направлениями саморазвития)."""
from datetime import date

from utils import get_next_id


def get_interest(interests: dict[int, dict], interest_id: int) -> dict:
    """Вернуть интерес по номеру; если его нет, вызвать ValueError."""
    if interest_id not in interests:
        raise ValueError(f"Интерес с номером {interest_id} не найден")
    return interests[interest_id]


def is_interest_active(interests: dict[int, dict], interest_id: int) -> bool:
    """Проверить, что интерес существует и не находится в архиве."""
    return interest_id in interests and interests[interest_id]["is_active"]


def add_interest(
    interests: dict[int, dict], name: str, category: str, weekly_goal: float
) -> dict:
    """Добавить интерес в словарь interests и вернуть созданную запись.

    Вызывает ValueError, если название или категория пусты
    или недельная цель не находится в диапазоне от 0 до 168 часов.
    """
    if not name.strip() or not category.strip():
        raise ValueError("Название и категория не могут быть пустыми")
    if not 0 < weekly_goal <= 168:
        raise ValueError(
            "Недельная цель должна быть больше 0 и не больше 168 ч"
        )
    interest_id = get_next_id(list(interests))
    interest = {
        "id": interest_id,
        "name": name.strip(),
        "category": category.strip(),
        "created_date": date.today().isoformat(),
        "is_active": True,
        "weekly_goal": weekly_goal,
    }
    interests[interest_id] = interest
    return interest


def find_interests(interests: dict[int, dict], query: str) -> list[dict]:
    """Найти интересы, в названии которых есть подстрока query.

    Регистр букв не учитывается.
    """
    query = query.strip().lower()
    matching = (
        interest
        for interest in interests.values()
        if query in interest["name"].lower()
    )
    return list(matching)


def sort_interests(interests: dict[int, dict]) -> list[dict]:
    """Вернуть интересы, отсортированные по недельной цели по убыванию."""
    return sorted(
        interests.values(),
        key=lambda interest: interest["weekly_goal"],
        reverse=True,
    )
