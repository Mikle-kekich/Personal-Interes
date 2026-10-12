"""Страницы подписок: список и карточка подписки."""
from django.http import HttpRequest, HttpResponse

from homepage.views import load_data, page
from models.subscriptions import find_subscription_by_id
from utils import format_date


def subscriptions(request: HttpRequest) -> HttpResponse:
    """Страница /subscriptions/: список подписок."""
    items = ""
    for subscription in load_data()["subscriptions"]:
        badge = "bg-secondary" if subscription.is_cancelled else "bg-success"
        text = (
            f"{subscription.user.name} – {subscription.interest.name}, "
            f"с {format_date(subscription.start_date)}"
        )
        items += f"""
<li class="list-group-item d-flex justify-content-between align-items-center">
<a href="/subscriptions/{subscription.id}/">{text}</a>
<span class="badge {badge} ms-2">{subscription.status}</span>
</li>
"""
    content = f"""
<h1>Подписки</h1>
<ul class="list-group">{items}</ul>
"""
    return HttpResponse(page("Interest Tracker – подписки", content))


def subscription_detail(
    request: HttpRequest, subscription_id: int
) -> HttpResponse:
    """Страница /subscriptions/<id>/: карточка подписки, если нет – 404."""
    subscription = find_subscription_by_id(
        load_data()["subscriptions"], subscription_id
    )
    if subscription is None:
        content = """
<h1 class="text-danger">Подписка не найдена</h1>
<a href="/subscriptions/" class="btn btn-outline-secondary">
← к списку подписок
</a>
"""
        return HttpResponse(
            page("Подписка не найдена", content),
            status=404,
        )

    interest = subscription.interest
    badge = "bg-secondary" if subscription.is_cancelled else "bg-success"
    content = f"""
<div class="card">
<div class="card-body">
<h5 class="card-title">Подписка №{subscription.id}</h5>
<p class="card-text">
<strong>Пользователь:</strong> {subscription.user.name}
</p>
<p class="card-text">
<strong>Интерес:</strong>
<a href="/interests/{interest.id}/">{interest.name}</a>
</p>
<p class="card-text">
<strong>Категория:</strong> {interest.category.name}
</p>
<p class="card-text">
<strong>Дата подписки:</strong> {format_date(subscription.start_date)}
</p>
<p class="card-text">
<strong>Отмечено часов:</strong> {subscription.get_total_hours():.1f} ч
</p>
<p class="card-text">
Статус: <span class="badge {badge}">{subscription.status}</span>
</p>
<a href="/subscriptions/" class="btn btn-outline-secondary">
← к списку подписок
</a>
</div>
</div>
"""
    return HttpResponse(
        page(f"Подписка №{subscription.id}", content),
        status=200,
    )
