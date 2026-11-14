"""Страницы интересов: список, поиск доступных интересов и карточка.

Данные берутся из базы через Django ORM (модели Category, Interest,
User и Subscription), прямые SQL-запросы в представлениях не используются.
"""
import re

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from datetime import date

from interests.models import Category, Interest
from subscriptions.models import Subscription
from users.models import User


def interests(request: HttpRequest) -> HttpResponse:
    """Страница /interests/: список интересов.

    Параметр ?category=<номер> оставляет интересы одной категории,
    параметр ?q=<текст> – интересы, в названии которых или в названии
    категории есть этот текст.
    """
    category_id = request.GET.get("category", "").strip()
    query = request.GET.get("q", "").strip()
    interests_data = Interest.objects.select_related("category")
    if category_id.isdecimal():
        # category__id (а не category_id): слишком большое число
        # даёт пустой результат, а не ошибку базы данных.
        interests_data = interests_data.filter(category__id=int(category_id))
    if query:
        # SQLite сравнивает без учёта регистра только латиницу (LIKE),
        # поэтому вместо icontains используется iregex: он работает
        # и для кириллицы. re.escape превращает текст в обычную подстроку.
        pattern = re.escape(query)
        interests_data = interests_data.filter(
            Q(name__iregex=pattern) | Q(category__name__iregex=pattern)
        )
    context = {
        "interests": interests_data.order_by("name"),
        "categories": Category.objects.order_by("name"),
        "category_id": category_id,
        "q": query,
    }
    return render(request, "interests/interest_list.html", context)


def available_interests(request: HttpRequest) -> HttpResponse:
    """Страница /interests/available/: интересы, доступные пользователю.

    Номер пользователя берётся из параметра ?user=<номер>. Если параметра
    нет, поиск не выполняется: страница показывает только форму.
    """
    user_id = request.GET.get("user", "").strip()
    selected_user = None
    selected_date = request.GET.get("date", "").strip()
    error = None
    as_of = None
    if selected_date:
        try:
            as_of = date.fromisoformat(selected_date)
        except ValueError:
            error = "Укажите корректную дату."
    interests_data = []
    if user_id.isdecimal():
        try:
            selected_user = User.objects.get(pk=int(user_id))
        except User.DoesNotExist:
            selected_user = None
    if selected_user is not None and error is None:
        # Номера интересов, на которые у пользователя есть активная подписка.
        subscriptions = Subscription.objects.active().filter(
            user=selected_user
        )
        # Подписка действует с даты начала; это не бронь на отдельный день.
        if as_of is not None:
            subscriptions = subscriptions.filter(start_date__lte=as_of)
        subscribed_ids = subscriptions.values_list("interest_id", flat=True)
        interests_data = (
            Interest.objects.select_related("category")
            .filter(is_active=True)
            .exclude(pk__in=subscribed_ids)
            .order_by("name")
        )
    context = {
        "users": User.objects.order_by("name"),
        "user_id": user_id,
        "selected_user": selected_user,
        "selected_date": selected_date,
        "error": error,
        "interests": interests_data,
    }
    return render(request, "interests/available.html", context)


def interest_detail(
    request: HttpRequest, interest_id=None, slug=None
) -> HttpResponse:
    """Карточка по slug; прежний числовой адрес сохранён."""
    lookup = {"slug": slug} if slug is not None else {"pk": interest_id}
    interest = get_object_or_404(
        Interest.objects.select_related("category"),
        **lookup,
    )
    subscribed_users = set(
        interest.subscriptions.active().values_list("user_id", flat=True)
    )
    users_info = []
    for user in User.objects.order_by("name"):
        users_info.append(
            {
                "user": user,
                "allowed": (
                    interest.is_active and user.pk not in subscribed_users
                ),
            }
        )
    context = {
        "interest": interest,
        "users_info": users_info,
    }
    return render(request, "interests/interest_detail.html", context)
