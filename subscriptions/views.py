"""Страницы подписок: список и карточка подписки."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from homepage.views import load_data
from models.subscriptions import find_subscription_by_id


def subscriptions(request: HttpRequest) -> HttpResponse:
    """Страница /subscriptions/: список подписок."""
    context = {
        "subscriptions": load_data()["subscriptions"],
    }
    return render(request, "subscriptions/subscription_list.html", context)


def subscription_detail(
    request: HttpRequest, subscription_id: int
) -> HttpResponse:
    """Страница /subscriptions/<id>/: карточка подписки, если нет – 404."""
    subscription = find_subscription_by_id(
        load_data()["subscriptions"], subscription_id
    )
    context = {
        "subscription": subscription,
    }
    return render(
        request,
        "subscriptions/subscription_detail.html",
        context,
        status=404 if subscription is None else 200,
    )
