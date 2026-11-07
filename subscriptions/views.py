"""Страницы подписок: список, статистика и карточка подписки.

Данные берутся из базы через Django ORM (модели Subscription, Activity,
Interest и Category), прямые SQL-запросы в представлениях не используются.
"""
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from interests.models import Category, Interest
from subscriptions.models import Activity, Subscription
from users.models import User


def subscriptions(request: HttpRequest) -> HttpResponse:
    """Страница /subscriptions/: активные подписки.

    Необязательные параметры запроса: ?date=ГГГГ-ММ-ДД (дата подписки),
    ?interest=<номер>, ?user=<номер>, ?sort=date|interest|user (порядок)
    и ?page=<номер> (страница, по 3 подписки на странице).
    """
    start_date = request.GET.get("date", "").strip()
    interest_id = request.GET.get("interest", "").strip()
    user_id = request.GET.get("user", "").strip()
    sort = request.GET.get("sort", "date")
    error = None

    subscriptions_data = Subscription.objects.filter(is_cancelled=False)
    if start_date:
        try:
            selected_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            subscriptions_data = subscriptions_data.filter(
                start_date=selected_date
            )
    # Фильтры по полю связанной модели (interest__id, user__id): слишком
    # большое число даёт пустой результат, а не ошибку базы данных.
    if interest_id.isdecimal():
        subscriptions_data = subscriptions_data.filter(
            interest__id=int(interest_id)
        )
    if user_id.isdecimal():
        subscriptions_data = subscriptions_data.filter(user__id=int(user_id))

    # Поле сортировки выбирается из заданного набора, а не берётся
    # из адресной строки напрямую.
    sort_fields = {
        "date": "start_date",
        "interest": "interest__name",
        "user": "user__name",
    }
    sort_field = sort_fields.get(sort, "start_date")
    subscriptions_data = (
        subscriptions_data
        .annotate(
            user_name=F("user__name"),
            interest_name=F("interest__name"),
        )
        .values(
            "id",
            "user_name",
            "interest_name",
            "start_date",
            "is_cancelled",
        )
        .order_by(sort_field, "id")
    )

    paginator = Paginator(subscriptions_data, 3)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "subscriptions": page_obj,
        "page_obj": page_obj,
        "subscriptions_count": Subscription.objects.filter(
            is_cancelled=False
        ).count(),
        "start_date": start_date,
        "selected_interest": interest_id,
        "selected_user": user_id,
        "sort": sort,
        "interests": Interest.objects.order_by("name"),
        "users": User.objects.order_by("name"),
        "error": error,
    }
    return render(request, "subscriptions/subscription_list.html", context)


def statistics(request: HttpRequest) -> HttpResponse:
    """Страница /subscriptions/statistics/: статистика из базы."""
    totals = Activity.objects.aggregate(
        activities_count=Count("id"),
        total_hours=Coalesce(Sum("hours"), 0.0),
    )
    # Запросы строятся от Interest и Category, поэтому интересы
    # и категории без связанных записей остаются в результате (со счётом 0).
    subscriptions_by_interest = (
        Interest.objects
        .annotate(
            subscriptions_count=Count(
                "subscriptions",
                filter=Q(subscriptions__is_cancelled=False),
            ),
            interest_name=F("name"),
        )
        .values("interest_name", "subscriptions_count")
        .order_by("-subscriptions_count", "interest_name")
    )
    # Часы считаются по всем подпискам, включая отменённые.
    hours_by_interest = (
        Interest.objects
        .annotate(
            total_hours=Coalesce(Sum("subscriptions__activities__hours"), 0.0),
            interest_name=F("name"),
        )
        .values("interest_name", "total_hours")
        .order_by("-total_hours", "interest_name")
    )
    interests_by_category = (
        Category.objects
        .annotate(
            interests_count=Count("interests"),
            category_name=F("name"),
        )
        .values("category_name", "interests_count")
        .order_by("-interests_count", "category_name")
    )
    popular_categories = interests_by_category.filter(interests_count__gt=1)
    context = {
        "totals": totals,
        "subscriptions_by_interest": subscriptions_by_interest,
        "hours_by_interest": hours_by_interest,
        "interests_by_category": interests_by_category,
        "popular_categories": popular_categories,
    }
    return render(request, "subscriptions/statistics.html", context)


def subscription_detail(
    request: HttpRequest, subscription_id: int
) -> HttpResponse:
    """Страница /subscriptions/<id>/: карточка подписки, если нет – 404."""
    subscription = get_object_or_404(
        Subscription.objects.select_related("user", "interest__category"),
        pk=subscription_id,
    )
    context = {
        "subscription": subscription,
    }
    return render(request, "subscriptions/subscription_detail.html", context)
