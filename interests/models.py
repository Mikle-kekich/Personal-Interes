from django.db import models


class Category(models.Model):
    """Категория (сфера) интересов, например «Спорт» или «Языки»."""

    name = models.CharField(
        max_length=100,
        verbose_name="Название категории",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Interest(models.Model):
    """Интерес (хобби или направление саморазвития) из одной категории.

    Интерес в архиве (is_active = False) недоступен для новых подписок.
    """

    name = models.CharField(
        max_length=200,
        verbose_name="Название интереса",
    )
    # Категорию с интересами удалить нельзя: PROTECT сохраняет данные.
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="interests",
        verbose_name="Категория",
    )
    weekly_goal = models.FloatField(
        verbose_name="План на неделю, ч",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Интерес активен",
    )

    def can_subscribe(self, user):
        """Проверить, можно ли подписать пользователя на этот интерес.

        Нельзя подписаться на интерес в архиве и нельзя иметь две
        активные подписки одного пользователя на один интерес.
        Отменённая подписка повторной подписке не мешает.
        """
        if not self.is_active:
            return False
        return not self.subscriptions.filter(
            user=user,
            is_cancelled=False,
        ).exists()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Интерес"
        verbose_name_plural = "Интересы"
