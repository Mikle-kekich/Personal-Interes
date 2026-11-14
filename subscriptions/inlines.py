from django.contrib import admin

from subscriptions.models import Subscription


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    fields = ("user", "interest", "start_date", "status")
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "interest")
