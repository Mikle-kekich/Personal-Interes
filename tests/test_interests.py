"""Тесты функций работы с интересами."""
from interests import add_interest, find_interests


def test_add_interest():
    """Интерес добавляется в словарь под номером 1."""
    interests = {}
    add_interest(interests, "Гитара", "Творчество", 5)
    assert len(interests) == 1
    assert interests[1]["name"] == "Гитара"


def test_find_interests():
    """Поиск по части названия не зависит от регистра букв."""
    interests = {}
    add_interest(interests, "Изучение Python", "Программирование", 8)
    add_interest(interests, "Бег", "Спорт", 4)
    assert len(find_interests(interests, "python")) == 1
