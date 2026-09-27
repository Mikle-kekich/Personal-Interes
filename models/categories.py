"""Класс Category и функции работы с категориями интересов."""
from typing import List, Optional

from utils import get_next_id


class Category:
    """Категория (сфера) интересов, например «Спорт» или «Языки»."""

    def __init__(self, category_id: int, name: str) -> None:
        """Создать объект категории."""
        self.id = category_id
        self.name = name

    def __str__(self) -> str:
        """Вернуть строковое представление категории."""
        return f"{self.id}. {self.name}"


def add_category(categories: List[Category], name: str) -> Category:
    """Создать категорию, добавить её в список и вернуть.

    Вызывает ValueError, если название пустое.
    """
    if not name.strip():
        raise ValueError("Название категории не может быть пустым")
    category = Category(
        get_next_id([item.id for item in categories]), name.strip()
    )
    categories.append(category)
    return category


def find_category_by_id(
    categories: List[Category], category_id: int
) -> Optional[Category]:
    """Найти категорию по номеру; если её нет, вернуть None."""
    for category in categories:
        if category.id == category_id:
            return category
    return None


def show_categories(categories: List[Category]) -> None:
    """Вывести список категорий."""
    if not categories:
        print("Категорий пока нет.")
        return
    for category in categories:
        print(category)
