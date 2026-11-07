from django.db import models
from django.db.models import Sum

from interests.models import Interest
from users.models import User


class Subscription(models.Model):
    """Подписка пользователя на интерес с журналом занятий."""

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
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name="Подписка отменена",
    )

    def cancel(self):
        """Отменить подписку: сохраняется только поле is_cancelled."""
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])

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
