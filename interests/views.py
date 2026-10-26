"""Страницы интересов: список, поиск доступных интересов и карточка.

Список и поиск получают данные из базы SQLite SQL-запросами (ПР7),
карточка интереса по-прежнему работает с JSON-файлами (ПР5–ПР6).
"""
import sqlite3

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from homepage.views import load_data
from models.interests import find_interest_by_id
from models.subscriptions import can_subscribe


def interests(request: HttpRequest) -> HttpResponse:
    """Страница /interests/: список интересов из базы SQLite.

    Параметр ?category=<номер> оставляет интересы одной категории.
    """
    category_id = request.GET.get("category")
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    categories = conn.execute("""
        SELECT
            id,
            name
        FROM categories
        ORDER BY name;
    """).fetchall()
    if category_id:
        interests_data = conn.execute("""
            SELECT
                interests.id,
                interests.name,
                categories.name AS category_name,
                interests.weekly_goal,
                interests.is_active
            FROM interests
            JOIN categories
                ON interests.category_id = categories.id
            WHERE interests.category_id = ?
            ORDER BY interests.name;
        """, [category_id]).fetchall()
    else:
        interests_data = conn.execute("""
            SELECT
                interests.id,
                interests.name,
                categories.name AS category_name,
                interests.weekly_goal,
                interests.is_active
            FROM interests
            JOIN categories
                ON interests.category_id = categories.id
            ORDER BY interests.name;
        """).fetchall()
    conn.close()
    context = {
        "interests": interests_data,
        "categories": categories,
        "category_id": category_id,
    }
    return render(request, "interests/interest_list.html", context)


def available_interests(request: HttpRequest) -> HttpResponse:
    """Страница /interests/available/: интересы, доступные пользователю.

    Номер пользователя берётся из параметра ?user=<номер>. Если параметра
    нет, запросы поиска не выполняются: страница показывает только форму.
    """
    user_id = request.GET.get("user")
    selected_user = None
    interests_data = []
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    users = conn.execute("""
        SELECT
            id,
            name,
            email
        FROM users
        ORDER BY name;
    """).fetchall()
    if user_id:
        selected_user = conn.execute("""
            SELECT
                id,
                name,
                email
            FROM users
            WHERE id = ?;
        """, [user_id]).fetchone()
    if selected_user is not None:
        interests_data = conn.execute("""
            SELECT
                interests.id,
                interests.name,
                categories.name AS category_name,
                interests.weekly_goal,
                interests.is_active
            FROM interests
            JOIN categories
                ON interests.category_id = categories.id
            WHERE interests.is_active = 1
                AND interests.id NOT IN (
                    SELECT subscriptions.interest_id
                    FROM subscriptions
                    WHERE subscriptions.user_id = ?
                        AND subscriptions.is_cancelled = 0
                )
            ORDER BY interests.name;
        """, [selected_user["id"]]).fetchall()
    conn.close()
    context = {
        "users": users,
        "user_id": user_id,
        "selected_user": selected_user,
        "interests": interests_data,
    }
    return render(request, "interests/available.html", context)


def interest_detail(request: HttpRequest, interest_id: int) -> HttpResponse:
    """Страница /interests/<id>/: карточка интереса, если его нет – 404."""
    data = load_data()
    interest = find_interest_by_id(data["interests"], interest_id)
    users_info = []
    if interest is not None:
        for user in data["users"]:
            users_info.append(
                {
                    "user": user,
                    "allowed": can_subscribe(
                        data["subscriptions"], user, interest
                    ),
                }
            )
    context = {
        "interest": interest,
        "users_info": users_info,
    }
    return render(
        request,
        "interests/interest_detail.html",
        context,
        status=404 if interest is None else 200,
    )
