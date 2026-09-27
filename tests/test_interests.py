"""Тесты класса Interest и функций работы с интересами."""
from models import Category, Interest
from models.interests import (
    add_interest,
    filter_interests_by_category,
    find_interests,
)


def test_interest_creation():
    """Интерес хранит свои данные и ссылку на объект категории."""
    category = Category(2, "Спорт")
    interest = Interest(1, "Бег", category, 4)
    assert interest.id == 1
    assert interest.name == "Бег"
    assert interest.category is category
    assert interest.is_active
    assert str(interest) == "1. Бег [Спорт], план 4.0 ч в неделю, активен"


def test_validate_weekly_goal():
    """Недельная цель должна быть больше 0 и не больше 168 часов."""
    assert Interest.validate_weekly_goal(8)
    assert not Interest.validate_weekly_goal(0)
    assert not Interest.validate_weekly_goal(200)


def test_add_interest():
    """Функция создаёт объект Interest и добавляет его в список."""
    interests = []
    interest = add_interest(interests, "Гитара", Category(4, "Творчество"), 3)
    assert interests == [interest]
    assert interest.id == 1


def test_find_interests():
    """Поиск по части названия не зависит от регистра букв."""
    category = Category(1, "Программирование")
    interests = []
    add_interest(interests, "Изучение Python", category, 8)
    add_interest(interests, "Веб-разработка", category, 4)
    assert len(find_interests(interests, "python")) == 1


def test_filter_interests_by_category():
    """Отбираются только интересы выбранной категории."""
    sport = Category(2, "Спорт")
    interests = []
    add_interest(interests, "Бег", sport, 4)
    add_interest(interests, "Гитара", Category(4, "Творчество"), 3)
    result = filter_interests_by_category(interests, sport)
    assert [interest.name for interest in result] == ["Бег"]
