"""Страницы подписок: список, статистика и карточка подписки.

Список и статистика получают данные из базы SQLite SQL-запросами (ПР7),
карточка подписки по-прежнему работает с JSON-файлами (ПР5–ПР6).
"""
import sqlite3

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from homepage.views import load_data
from models.subscriptions import find_subscription_by_id


def subscriptions(request: HttpRequest) -> HttpResponse:
    """Страница /subscriptions/: активные подписки из базы SQLite."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    subscriptions_data = conn.execute("""
        SELECT
            subscriptions.id,
            users.name AS user_name,
            interests.name AS interest_name,
            subscriptions.start_date,
            subscriptions.is_cancelled
        FROM subscriptions
        JOIN users
            ON subscriptions.user_id = users.id
        JOIN interests
            ON subscriptions.interest_id = interests.id
        WHERE subscriptions.is_cancelled = 0
        ORDER BY subscriptions.start_date, subscriptions.id;
    """).fetchall()
    subscriptions_count = conn.execute("""
        SELECT
            COUNT(*) AS subscriptions_count
        FROM subscriptions
        WHERE is_cancelled = 0;
    """).fetchone()["subscriptions_count"]
    conn.close()
    context = {
        "subscriptions": subscriptions_data,
        "subscriptions_count": subscriptions_count,
    }
    return render(request, "subscriptions/subscription_list.html", context)


def statistics(request: HttpRequest) -> HttpResponse:
    """Страница /subscriptions/statistics/: статистика из базы SQLite."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    totals = conn.execute("""
        SELECT
            COUNT(*) AS activities_count,
            COALESCE(SUM(hours), 0) AS total_hours
        FROM activities;
    """).fetchone()
    subscriptions_by_interest = conn.execute("""
        SELECT
            interests.name AS interest_name,
            COUNT(subscriptions.id) AS subscriptions_count
        FROM interests
        LEFT JOIN subscriptions
            ON interests.id = subscriptions.interest_id
            AND subscriptions.is_cancelled = 0
        GROUP BY interests.id, interests.name
        ORDER BY subscriptions_count DESC, interests.name;
    """).fetchall()
    hours_by_interest = conn.execute("""
        SELECT
            interests.name AS interest_name,
            COALESCE(SUM(activities.hours), 0) AS total_hours
        FROM interests
        LEFT JOIN subscriptions
            ON interests.id = subscriptions.interest_id
        LEFT JOIN activities
            ON subscriptions.id = activities.subscription_id
        GROUP BY interests.id, interests.name
        ORDER BY total_hours DESC, interests.name;
    """).fetchall()
    interests_by_category = conn.execute("""
        SELECT
            categories.name AS category_name,
            COUNT(interests.id) AS interests_count
        FROM categories
        LEFT JOIN interests
            ON categories.id = interests.category_id
        GROUP BY categories.id, categories.name
        ORDER BY interests_count DESC, categories.name;
    """).fetchall()
    popular_categories = conn.execute("""
        SELECT
            categories.name AS category_name,
            COUNT(interests.id) AS interests_count
        FROM categories
        JOIN interests
            ON categories.id = interests.category_id
        GROUP BY categories.id, categories.name
        HAVING COUNT(interests.id) > 1
        ORDER BY interests_count DESC, categories.name;
    """).fetchall()
    conn.close()
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
