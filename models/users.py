"""Класс User и функции работы с пользователями."""
from typing import List, Optional

from utils import get_next_id


class User:
    """Пользователь системы, который подписывается на интересы."""

    def __init__(self, user_id: int, name: str, email: str) -> None:
        """Создать объект пользователя."""
        self.id = user_id
        self.name = name
        self.email = email

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из словаря с данными (запись из JSON)."""
        return cls(data["id"], data["name"], data["email"])

    def __str__(self) -> str:
        """Вернуть строковое представление пользователя."""
        return f"{self.id}. {self.name} <{self.email}>"


def add_user(users: List[User], name: str, email: str) -> User:
    """Создать пользователя, добавить его в список и вернуть.

    Вызывает ValueError, если имя пустое или в адресе почты нет «@».
    """
    if not name.strip():
        raise ValueError("Имя пользователя не может быть пустым")
    if "@" not in email:
        raise ValueError("Адрес электронной почты должен содержать @")
    user = User(
        get_next_id([item.id for item in users]), name.strip(), email.strip()
    )
    users.append(user)
    return user


def find_user(users: List[User], query: str) -> List[User]:
    """Найти пользователей, у которых query есть в имени или почте.

    Регистр букв не учитывается.
    """
    query = query.strip().lower()
    return [
        user
        for user in users
        if query in user.name.lower() or query in user.email.lower()
    ]


def find_user_by_id(users: List[User], user_id: int) -> Optional[User]:
    """Найти пользователя по номеру; если его нет, вернуть None."""
    for user in users:
        if user.id == user_id:
            return user
    return None


def show_users(users: List[User]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Пользователи не найдены.")
        return
    for user in users:
        print(user)
