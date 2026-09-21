"""Сохранение и загрузка данных проекта в JSON-файлах.

В файле хранится список словарей. Даты записаны строками ГГГГ-ММ-ДД.
"""
import json
from pathlib import Path


def _read_json(filename: Path) -> list[dict]:
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


def _write_json(filename: Path, records: list[dict]) -> None:
    """Записать список записей в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)


def load_interests(filename: Path) -> dict[int, dict]:
    """Загрузить интересы из JSON-файла в словарь {номер: интерес}."""
    return {interest["id"]: interest for interest in _read_json(filename)}


def save_interests(filename: Path, interests: dict[int, dict]) -> None:
    """Сохранить интересы в JSON-файл списком словарей."""
    _write_json(filename, list(interests.values()))


def load_activities(filename: Path) -> list[dict]:
    """Загрузить записи активности из JSON-файла."""
    return _read_json(filename)


def save_activities(filename: Path, activities: list[dict]) -> None:
    """Сохранить записи активности в JSON-файл."""
    _write_json(filename, activities)
