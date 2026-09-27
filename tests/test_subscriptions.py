"""Тесты класса Subscription и функций работы с подписками."""
from datetime import date

import pytest

from models import Category, Interest, Subscription, User
from models.subscriptions import (
    calculate_progress,
    create_subscription,
    generate_recommendation,
)


def make_user_and_interest():
    """Создать пользователя и активный интерес для тестов."""
    user = User(1, "Иван Петров", "ivan@example.com")
    interest = Interest(1, "Бег", Category(2, "Спорт"), 4)
    return user, interest


def test_subscription_creation():
    """Подписка хранит ссылки на объекты User и Interest."""
    user, interest = make_user_and_interest()
    subscription = Subscription(1, user, interest, "2026-09-14")
    assert subscription.user is user
    assert subscription.interest is interest
    assert subscription.interest.category.name == "Спорт"
    assert not subscription.is_cancelled
    assert str(subscription) == "1. Иван Петров — «Бег», с 14.09.2026, активна"


def test_subscription_cancel():
    """Метод cancel() меняет состояние подписки."""
    user, interest = make_user_and_interest()
    subscription = Subscription(1, user, interest, "2026-09-14")
    subscription.cancel()
    assert subscription.is_cancelled
    assert subscription.status == "отменена"


def test_second_active_subscription_forbidden():
    """Вторая активная подписка на тот же интерес не создаётся.

    После отмены первой подписки подписаться снова можно.
    """
    user, interest = make_user_and_interest()
    subscriptions = []
    first = create_subscription(subscriptions, user, interest)
    assert first is not None
    assert create_subscription(subscriptions, user, interest) is None
    first.cancel()
    assert create_subscription(subscriptions, user, interest) is not None
    assert len(subscriptions) == 2


def test_subscribe_to_archived_interest_forbidden():
    """На интерес в архиве подписаться нельзя."""
    user, interest = make_user_and_interest()
    interest.is_active = False
    subscriptions = []
    assert create_subscription(subscriptions, user, interest) is None
    assert subscriptions == []


def test_get_weekly_hours():
    """Считаются только часы за неделю 14-20 сентября 2026 года."""
    user, interest = make_user_and_interest()
    subscription = Subscription(1, user, interest, "2026-09-08")
    subscription.add_activity(date(2026, 9, 14), 2)
    subscription.add_activity(date(2026, 9, 18), 1.5)
    # занятие на прошлой неделе в сумму не входит
    subscription.add_activity(date(2026, 9, 10), 3)
    assert subscription.get_weekly_hours(date(2026, 9, 16)) == 3.5


def test_add_activity_to_cancelled_subscription_forbidden():
    """По отменённой подписке занятие отметить нельзя."""
    user, interest = make_user_and_interest()
    subscription = Subscription(1, user, interest, "2026-09-08")
    subscription.cancel()
    with pytest.raises(ValueError):
        subscription.add_activity(date(2026, 9, 15), 2)
    assert subscription.hours_by_date == {}


def test_calculate_progress():
    """6 часов из 8 - это 75 процентов недельной цели."""
    assert calculate_progress(6, 8) == 75.0


def test_generate_recommendation_goal_reached():
    """При выполнении цели выводится поздравление."""
    text = generate_recommendation(True, 100.0, 8.0, 8.0)
    assert text == "Отличный результат! Недельная цель полностью выполнена."
