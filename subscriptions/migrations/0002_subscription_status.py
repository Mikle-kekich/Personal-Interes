from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("subscriptions", "0001_initial")]
    operations = [migrations.AddField(
        model_name="subscription", name="status",
        field=models.CharField(
            max_length=10, default="ACTIVE", verbose_name="Статус",
            choices=[("ACTIVE", "Активна"), ("CANCELLED", "Отменена"),
                     ("COMPLETED", "Завершена")],
        ),
    )]
