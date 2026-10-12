from django.urls import path

from . import views

urlpatterns = [
    path("", views.interests, name="interests"),
    path("<int:interest_id>/", views.interest_detail, name="interest_detail"),
]
