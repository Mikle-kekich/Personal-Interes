"""Тесты функций учёта активности."""
from datetime import date

import pytest

from activities import (
    add_activity,
    calculate_progress,
    cancel_activity,
    generate_recommendation,
    get_weekly_hours,
)
from interests import add_interest


def make_interests():
    """Создать словарь с одним активным интересом под номером 1."""
    interests = {}
    add_interest(interests, "Бег", "Спорт", 4)
    return interests


def test_add_activity():
    """Запись активности добавляется в список."""
    activities = []
    add_activity(activities, make_interests(), 1, date(2026, 9, 15), 2)
    assert len(activities) == 1


def test_add_activity_for_archived_interest_forbidden():
    """Для интереса в архиве запись активности создать нельзя."""
    interests = make_interests()
    interests[1]["is_active"] = False
    activities = []
    with pytest.raises(ValueError):
        add_activity(activities, interests, 1, date(2026, 9, 15), 2)
    assert activities == []


def test_cancel_activity():
    """Отменённая запись удаляется из списка."""
    activities = []
    add_activity(activities, make_interests(), 1, date(2026, 9, 15), 2)
    cancel_activity(activities, 1)
    assert activities == []


def test_get_weekly_hours():
    """Считаются только часы за неделю 14-20 сентября 2026 года."""
    interests = make_interests()
    activities = []
    add_activity(activities, interests, 1, date(2026, 9, 14), 2)
    add_activity(activities, interests, 1, date(2026, 9, 18), 1.5)
    # запись за прошлую неделю в сумму не входит
    add_activity(activities, interests, 1, date(2026, 9, 10), 3)
    assert get_weekly_hours(activities, 1, date(2026, 9, 16)) == 3.5


def test_calculate_progress():
    """6 часов из 8 - это 75 процентов недельной цели."""
    assert calculate_progress(6, 8) == 75.0


def test_generate_recommendation_goal_reached():
    """При выполнении цели выводится поздравление."""
    text = generate_recommendation(True, 100.0, 8.0, 8.0)
    assert text == "Отличный результат! Недельная цель полностью выполнена."
