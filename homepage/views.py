"""Главная страница, страница ошибки 404 и загрузка данных для веб-слоя."""
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from storage import (
    load_categories,
    load_interests,
    load_subscriptions,
    load_users,
)

DATA_DIR = settings.BASE_DIR / "data"


def load_data() -> dict:
    """Загрузить данные проекта из JSON-файлов, как это делает main.py.

    Возвращает словарь со списками объектов ПР3: категории, интересы,
    пользователи и подписки (подписка связана с пользователем и интересом).
    """
    categories = load_categories(DATA_DIR / "categories.json")
    interests = load_interests(DATA_DIR / "interests.json", categories)
    users = load_users(DATA_DIR / "users.json")
    subscriptions = load_subscriptions(
        DATA_DIR / "subscriptions.json", users, interests
    )
    return {
        "categories": categories,
        "interests": interests,
        "users": users,
        "subscriptions": subscriptions,
    }


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница /: описание приложения и кнопки-ссылки."""
    return render(request, "homepage/index.html")


def page_not_found(
    request: HttpRequest, exception: Exception
) -> HttpResponse:
    """Обработчик ошибки 404 (handler404): адреса нет среди маршрутов."""
    return render(request, "homepage/page_not_found.html", status=404)
