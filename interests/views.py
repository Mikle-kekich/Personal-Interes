"""Страницы интересов: список и карточка интереса."""
from django.http import HttpRequest, HttpResponse

from homepage.views import load_data, page
from models.interests import find_interest_by_id
from models.subscriptions import can_subscribe


def interests(request: HttpRequest) -> HttpResponse:
    """Страница /interests/: список интересов из data/interests.json."""
    items = ""
    for interest in load_data()["interests"]:
        status = "активен" if interest.is_active else "в архиве"
        badge = "bg-success" if interest.is_active else "bg-secondary"
        text = (
            f"{interest.name} – {interest.category.name}, "
            f"план {interest.weekly_goal:.1f} ч в неделю"
        )
        items += f"""
<li class="list-group-item d-flex justify-content-between align-items-center">
<a href="/interests/{interest.id}/">{text}</a>
<span class="badge {badge} ms-2">{status}</span>
</li>
"""
    content = f"""
<h1>Интересы</h1>
<ul class="list-group">{items}</ul>
"""
    return HttpResponse(page("Interest Tracker – интересы", content))


def interest_detail(request: HttpRequest, interest_id: int) -> HttpResponse:
    """Страница /interests/<id>/: карточка интереса, если его нет – 404."""
    data = load_data()
    interest = find_interest_by_id(data["interests"], interest_id)
    if interest is None:
        content = """
<h1 class="text-danger">Интерес не найден</h1>
<a href="/interests/" class="btn btn-outline-secondary">
← к списку интересов
</a>
"""
        return HttpResponse(
            page("Интерес не найден", content),
            status=404,
        )

    status = "активен" if interest.is_active else "в архиве"
    badge = "bg-success" if interest.is_active else "bg-secondary"
    users = ""
    for user in data["users"]:
        allowed = can_subscribe(data["subscriptions"], user, interest)
        user_text = "можно подписаться" if allowed else "подписка невозможна"
        user_badge = "bg-success" if allowed else "bg-danger"
        users += f"""
<li class="list-group-item d-flex justify-content-between align-items-center">
{user.name}
<span class="badge {user_badge} ms-2">{user_text}</span>
</li>
"""
    content = f"""
<div class="card">
<div class="card-body">
<h5 class="card-title">{interest.name}</h5>
<p class="card-text">
<strong>ID:</strong> {interest.id}
</p>
<p class="card-text">
<strong>Категория:</strong> {interest.category.name}
</p>
<p class="card-text">
<strong>План на неделю:</strong> {interest.weekly_goal:.1f} ч
</p>
<p class="card-text">
Статус: <span class="badge {badge}">{status}</span>
</p>
<p class="card-text"><strong>Подписка пользователей:</strong></p>
<ul class="list-group mb-3">{users}</ul>
<a href="/interests/" class="btn btn-outline-secondary">
← к списку интересов
</a>
</div>
</div>
"""
    return HttpResponse(
        page(interest.name, content),
        status=200,
    )
