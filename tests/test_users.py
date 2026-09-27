"""Тесты класса User."""
from models import User


def test_user_creation():
    """Пользователь хранит переданные данные и выводится строкой."""
    user = User(1, "Иван Петров", "ivan@example.com")
    assert user.id == 1
    assert user.name == "Иван Петров"
    assert user.email == "ivan@example.com"
    assert str(user) == "1. Иван Петров <ivan@example.com>"


def test_user_from_data():
    """Метод класса from_data() создаёт пользователя из словаря JSON."""
    data = {"id": 2, "name": "Анна Смирнова", "email": "anna@example.com"}
    user = User.from_data(data)
    assert isinstance(user, User)
    assert user.id == 2
    assert user.name == "Анна Смирнова"
