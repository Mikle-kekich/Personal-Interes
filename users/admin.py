from django.contrib import admin

from subscriptions.inlines import SubscriptionInline
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")
    list_display_links = ("id", "name")
    search_fields = ("name", "email")
    ordering = ("name", "pk")
    list_per_page = 10
    inlines = (SubscriptionInline,)
