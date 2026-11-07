"""Главная страница и страница ошибки 404."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница /: описание приложения и кнопки-ссылки."""
    return render(request, "homepage/index.html")


def page_not_found(
    request: HttpRequest, exception: Exception
) -> HttpResponse:
    """Обработчик ошибки 404 (handler404): адреса нет среди маршрутов."""
    return render(request, "homepage/page_not_found.html", status=404)
