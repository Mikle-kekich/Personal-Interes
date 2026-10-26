from django.urls import path

from . import views

app_name = "interests"

urlpatterns = [
    path("", views.interests, name="list"),
    path("available/", views.available_interests, name="available"),
    path("<int:interest_id>/", views.interest_detail, name="detail"),
]
