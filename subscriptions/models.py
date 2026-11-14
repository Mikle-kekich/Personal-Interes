from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError

from interests.models import Interest
from users.models import User


class SubscriptionQuerySet(models.QuerySet):
    """Повторно используемые фильтры подписок без выполнения запроса."""

    def active(self):
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, selected_date):
        return self.filter(start_date=selected_date)


class SubscriptionManager(models.Manager.from_queryset(SubscriptionQuerySet)):
    pass


class Subscription(models.Model):
    """Подписка пользователя на интерес с журналом занятий."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Активна"
        CANCELLED = "CANCELLED", "Отменена"
        COMPLETED = "COMPLETED", "Завершена"

    objects = SubscriptionManager()

    # PROTECT: пока есть подписки, пользователя и интерес не удалить,
    # поэтому история подписок сохраняется.
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    interest = models.ForeignKey(
        Interest,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name="Интерес",
    )
    start_date = models.DateField(
        verbose_name="Дата подписки",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE,
        verbose_name="Статус",
    )

    def clean(self):
        super().clean()
        if (self.status == self.Status.ACTIVE and self.interest_id
                and not self.interest.is_active):
            raise ValidationError({
                "interest": "Нельзя активировать подписку на архивный интерес."
            })

    def cancel(self):
        """Отменить подписку с сохранением истории занятий."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def get_total_hours(self):
        """Посчитать все часы, отмеченные по подписке.

        Если занятий нет, сумма не определена (None), поэтому
        возвращается 0.
        """
        total = self.activities.aggregate(total=Sum("hours"))["total"]
        return total or 0

    def __str__(self):
        return f"{self.user} – {self.interest} (с {self.start_date})"

    class Meta:
        ordering = ["start_date", "pk"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "interest"],
                condition=models.Q(status="ACTIVE"),
                name="unique_active_user_interest",
                violation_error_message=(
                    "Уже есть активная подписка на интерес."
                ),
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=[
                    "ACTIVE", "CANCELLED", "COMPLETED"
                ]),
                name="valid_subscription_status",
            ),
        ]


class Activity(models.Model):
    """Занятие по подписке: дата и затраченные часы.

    В JSON занятия лежат внутри подписки (словарь hours_by_date),
    в базе одна запись таблицы – одно занятие.
    """

    # CASCADE: занятия – часть подписки и без неё не нужны.
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="Подписка",
    )
    activity_date = models.DateField(
        verbose_name="Дата занятия",
    )
    hours = models.FloatField(
        verbose_name="Затрачено часов",
    )

    def __str__(self):
        return f"{self.activity_date}: {self.hours} ч"

    class Meta:
        ordering = ["activity_date", "pk"]
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
