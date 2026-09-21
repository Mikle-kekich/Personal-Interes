"""Тесты сохранения и загрузки данных."""
from interests import add_interest
from storage import load_interests, save_interests


def test_save_and_load_interests(tmp_path):
    """Сохранённые в JSON интересы загружаются без изменений."""
    interests = {}
    add_interest(interests, "Изучение Python", "Программирование", 8)
    filename = tmp_path / "interests.json"
    save_interests(filename, interests)
    assert load_interests(filename) == interests


def test_load_interests_missing_file(tmp_path):
    """Если файла нет, загружается пустой словарь и ошибки нет."""
    assert load_interests(tmp_path / "no_file.json") == {}
