from django.contrib import admin

from interests.models import Category, Interest
from subscriptions.inlines import SubscriptionInline

admin.site.site_header = "Управление личными интересами"
admin.site.site_title = "Personal-Interes"
admin.site.index_title = "Администрирование системы"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name", "pk")
    list_per_page = 10


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "category", "weekly_goal", "is_active", "is_intensive"
    )
    list_display_links = ("id", "name")
    search_fields = ("name", "category__name")
    list_filter = ("is_active", "is_intensive", "category")
    ordering = ("name", "pk")
    list_per_page = 10
    list_select_related = ("category",)
    readonly_fields = ("slug", "is_intensive")
    inlines = (SubscriptionInline,)
