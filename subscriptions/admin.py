from django.contrib import admin

from subscriptions.models import Activity, Subscription


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "interest", "start_date", "status")
    list_display_links = ("id",)
    search_fields = ("user__name", "user__email", "interest__name")
    list_filter = ("status", "start_date", "interest", "user")
    ordering = ("-start_date", "pk")
    list_per_page = 10
    list_select_related = ("user", "interest")
    date_hierarchy = "start_date"
    autocomplete_fields = ("user", "interest")
    inlines = (ActivityInline,)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "subscription", "activity_date", "hours")
    list_filter = ("activity_date",)
    search_fields = (
        "subscription__user__name", "subscription__interest__name"
    )
    ordering = ("-activity_date", "pk")
    list_per_page = 10
    list_select_related = ("subscription__user", "subscription__interest")
