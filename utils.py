"""Вспомогательные функции: безопасный ввод и работа с датами."""
from datetime import date, datetime

DATE_FORMAT = "%d.%m.%Y"


def input_int(prompt: str) -> int:
    """Запросить целое число; при некорректном вводе повторить запрос."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число.")


def input_float(prompt: str) -> float:
    """Запросить число (можно с запятой); при ошибке повторить запрос."""
    while True:
        try:
            return float(input(prompt).replace(",", "."))
        except ValueError:
            print("Ошибка: введите число, например 1.5.")


def input_date(prompt: str) -> date:
    """Запросить дату в формате ДД.ММ.ГГГГ; при ошибке повторить запрос."""
    while True:
        try:
            return datetime.strptime(input(prompt).strip(), DATE_FORMAT).date()
        except ValueError:
            print("Ошибка: введите дату в формате ДД.ММ.ГГГГ.")


def format_date(iso_date: str) -> str:
    """Преобразовать дату из формата ГГГГ-ММ-ДД (как в JSON) в ДД.ММ.ГГГГ."""
    return date.fromisoformat(iso_date).strftime(DATE_FORMAT)


def get_next_id(ids: list[int]) -> int:
    """Вернуть следующий номер: наибольший из имеющихся плюс 1."""
    return max(ids, default=0) + 1
