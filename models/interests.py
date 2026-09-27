"""Класс Interest и функции работы с коллекцией интересов."""
from typing import List, Optional

from utils import get_next_id

from .categories import Category


class Interest:
    """Интерес (хобби или направление саморазвития) из какой-то категории."""

    def __init__(
        self,
        interest_id: int,
        name: str,
        category: Category,
        weekly_goal: float,
    ) -> None:
        """Создать объект интереса.

        Новый интерес активен. Интерес в архиве (is_active = False)
        недоступен для новых подписок.
        """
        self.id = interest_id
        self.name = name
        self.category = category
        self.weekly_goal = weekly_goal
        self.is_active = True

    @staticmethod
    def validate_weekly_goal(weekly_goal: float) -> bool:
        """Проверить, что недельная цель больше 0 и не больше 168 ч."""
        return 0 < weekly_goal <= 168

    def __str__(self) -> str:
        """Вернуть строковое представление интереса."""
        status = "активен" if self.is_active else "в архиве"
        return (
            f"{self.id}. {self.name} [{self.category.name}], "
            f"план {self.weekly_goal:.1f} ч в неделю, {status}"
        )


def add_interest(
    interests: List[Interest],
    name: str,
    category: Category,
    weekly_goal: float,
) -> Interest:
    """Создать интерес, добавить его в список и вернуть.

    Вызывает ValueError, если название пустое или недельная цель
    не находится в диапазоне от 0 до 168 часов.
    """
    if not name.strip():
        raise ValueError("Название интереса не может быть пустым")
    if not Interest.validate_weekly_goal(weekly_goal):
        raise ValueError(
            "Недельная цель должна быть больше 0 и не больше 168 ч"
        )
    interest = Interest(
        get_next_id([item.id for item in interests]),
        name.strip(),
        category,
        weekly_goal,
    )
    interests.append(interest)
    return interest


def find_interests(interests: List[Interest], query: str) -> List[Interest]:
    """Найти интересы, в названии которых есть подстрока query.

    Регистр букв не учитывается.
    """
    query = query.strip().lower()
    matching = (
        interest
        for interest in interests
        if query in interest.name.lower()
    )
    return list(matching)


def filter_interests_by_category(
    interests: List[Interest], category: Category
) -> List[Interest]:
    """Отобрать интересы указанной категории."""
    return [
        interest
        for interest in interests
        if interest.category.id == category.id
    ]


def sort_interests(interests: List[Interest]) -> List[Interest]:
    """Вернуть интересы, отсортированные по недельной цели по убыванию."""
    return sorted(
        interests,
        key=lambda interest: interest.weekly_goal,
        reverse=True,
    )


def find_interest_by_id(
    interests: List[Interest], interest_id: int
) -> Optional[Interest]:
    """Найти интерес по номеру; если его нет, вернуть None."""
    for interest in interests:
        if interest.id == interest_id:
            return interest
    return None


def show_interests(interests: List[Interest]) -> None:
    """Вывести список интересов."""
    if not interests:
        print("Интересы не найдены.")
        return
    for interest in interests:
        print(interest)
