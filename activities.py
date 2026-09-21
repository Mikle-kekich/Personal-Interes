"""Функции для учёта активности: записи занятий, прогресс и статистика.

Здесь же находятся функции расчёта прогресса и рекомендаций
из начального сценария ПР1.
"""
from datetime import date

from interests import is_interest_active
from utils import get_next_id


def add_activity(
    activities: list[dict],
    interests: dict[int, dict],
    interest_id: int,
    activity_date: date,
    hours: float,
) -> dict:
    """Добавить запись активности в список activities и вернуть её.

    Вызывает ValueError, если интерес не найден или находится в архиве
    (учёт времени приостановлен) либо время не в диапазоне от 0 до 24 ч.
    """
    if not is_interest_active(interests, interest_id):
        raise ValueError("Интерес не найден или находится в архиве")
    if not 0 < hours <= 24:
        raise ValueError("Время занятия должно быть больше 0 и не больше 24 ч")
    activity = {
        "id": get_next_id([item["id"] for item in activities]),
        "interest_id": interest_id,
        "activity_date": activity_date.isoformat(),
        "hours": hours,
    }
    activities.append(activity)
    return activity


def cancel_activity(activities: list[dict], activity_id: int) -> dict:
    """Отменить запись активности: удалить её из списка и вернуть.

    Вызывает ValueError, если записи с таким номером нет.
    """
    for activity in activities:
        if activity["id"] == activity_id:
            activities.remove(activity)
            return activity
    raise ValueError(f"Запись с номером {activity_id} не найдена")


def get_weekly_hours(
    activities: list[dict], interest_id: int, week_date: date
) -> float:
    """Посчитать часы по интересу за неделю, в которую входит week_date.

    Неделя определяется парой (год, номер недели) из isocalendar().
    """
    week = week_date.isocalendar()[:2]
    total = 0.0
    for activity in activities:
        activity_date = date.fromisoformat(activity["activity_date"])
        if (
            activity["interest_id"] == interest_id
            and activity_date.isocalendar()[:2] == week
        ):
            total += activity["hours"]
    return total


def calculate_progress(spent_hours: float, weekly_goal: float) -> float:
    """Рассчитать процент выполнения недельной цели (до десятых долей).

    Вызывает ValueError, если недельная цель не больше нуля.
    """
    if weekly_goal <= 0:
        raise ValueError("Недельная цель должна быть больше нуля")
    return round((spent_hours / weekly_goal) * 100, 1)


def generate_recommendation(
    is_active: bool,
    completion_rate: float,
    spent_hours: float,
    weekly_goal: float,
) -> str:
    """Проанализировать вовлечённость и сформировать рекомендацию."""
    if not is_active:
        return "Интерес находится в архиве. Учёт времени приостановлен."
    elif completion_rate >= 100.0:
        return "Отличный результат! Недельная цель полностью выполнена."
    elif completion_rate >= 50.0:
        remaining_hours: float = weekly_goal - spent_hours
        return (
            "Хороший темп. "
            f"До выполнения цели осталось {remaining_hours:.1f} ч."
        )
    else:
        remaining_hours: float = weekly_goal - spent_hours
        return (
            "Внимание: низкая активность. "
            f"Требуется уделить ещё {remaining_hours:.1f} ч."
        )


def get_statistics(
    interests: dict[int, dict], activities: list[dict]
) -> dict[str, float]:
    """Посчитать все затраченные часы по каждому интересу.

    Возвращает словарь {название интереса: часы}.
    """
    statistics = {}
    for interest in interests.values():
        statistics[interest["name"]] = sum(
            activity["hours"]
            for activity in activities
            if activity["interest_id"] == interest["id"]
        )
    return statistics
