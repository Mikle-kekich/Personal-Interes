from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode
from uuid import uuid4


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
    slug = models.SlugField(
        max_length=180, unique=True, editable=False,
        verbose_name="URL-идентификатор",
    )
    is_intensive = models.GeneratedField(
        expression=models.Case(
            models.When(weekly_goal__gte=5, then=models.Value(True)),
            default=models.Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Интенсивный план от 5 ч",
    )

    def save(self, *args, **kwargs):
        # UUID позволяет сразу выполнить один INSERT с уникальным slug.
        # Адрес сохраняется при переименовании интереса.
        if not self.slug:
            base = slugify(unidecode(self.name))[:140] or "interest"
            self.slug = f"{base}-{uuid4().hex}"
            if kwargs.get("update_fields") is not None:
                kwargs["update_fields"] = (
                    set(kwargs["update_fields"]) | {"slug"}
                )
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("interests:detail", kwargs={"slug": self.slug})

    def can_subscribe(self, user):
        """Проверить, можно ли подписать пользователя на этот интерес.

        Нельзя подписаться на интерес в архиве и нельзя иметь две
        активные подписки одного пользователя на один интерес.
        Отменённая подписка повторной подписке не мешает.
        """
        if not self.is_active:
            return False
        return not self.subscriptions.active().filter(user=user).exists()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Интерес"
        verbose_name_plural = "Интересы"
