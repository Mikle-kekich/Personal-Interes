"""Тесты сохранения и загрузки объектов в JSON."""
from datetime import date

from models import Category, Interest, Subscription, User
from storage import load_subscriptions, load_users, save_subscriptions


def test_save_and_load_subscriptions(tmp_path):
    """После загрузки подписка снова связана с объектами User и Interest."""
    user = User(1, "Иван Петров", "ivan@example.com")
    interest = Interest(1, "Бег", Category(2, "Спорт"), 4)
    subscription = Subscription(1, user, interest, "2026-09-14")
    subscription.add_activity(date(2026, 9, 15), 2)
    filename = tmp_path / "subscriptions.json"
    save_subscriptions(filename, [subscription])
    loaded = load_subscriptions(filename, [user], [interest])
    assert len(loaded) == 1
    assert loaded[0].user is user
    assert loaded[0].interest is interest
    assert loaded[0].hours_by_date == {"2026-09-15": 2}


def test_load_users_missing_file(tmp_path):
    """Если файла нет, загружается пустой список и ошибки нет."""
    assert load_users(tmp_path / "no_file.json") == []
