"""Главная страница и общие функции веб-слоя: каркас страницы и данные."""
from django.conf import settings
from django.http import HttpRequest, HttpResponse

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


def page(title: str, content: str) -> str:
    """Собрать HTML-страницу: кодировка, заголовок, Bootstrap, навигация."""
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{bootstrap}">
</head>
<body>
<nav class="nav">
<a class="nav-link" href="/">Главная</a>
<a class="nav-link" href="/interests/">Интересы</a>
<a class="nav-link" href="/subscriptions/">Подписки</a>
</nav>
<main class="container">{content}</main>
</body>
</html>"""


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница /: описание приложения и кнопки-ссылки."""
    content = """
<h1 class="display-4">Interest Tracker</h1>
<p class="lead">Система управления личными интересами.</p>
<p>Основные разделы:</p>
<a href="/interests/" class="btn btn-primary me-2">Интересы</a>
<a href="/subscriptions/" class="btn btn-secondary">Подписки</a>
"""
    return HttpResponse(page("Interest Tracker", content))
