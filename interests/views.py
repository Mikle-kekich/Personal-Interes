"""Страницы интересов: список и карточка интереса."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from homepage.views import load_data
from models.interests import find_interest_by_id
from models.subscriptions import can_subscribe


def interests(request: HttpRequest) -> HttpResponse:
    """Страница /interests/: список интересов из data/interests.json."""
    context = {
        "interests": load_data()["interests"],
    }
    return render(request, "interests/interest_list.html", context)


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
