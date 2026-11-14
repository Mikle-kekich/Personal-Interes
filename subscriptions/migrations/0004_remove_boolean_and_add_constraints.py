from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("subscriptions", "0003_transfer_statuses")]
    operations = [
        migrations.RemoveField("subscription", "is_cancelled"),
        migrations.AddConstraint(
            model_name="subscription",
            constraint=models.UniqueConstraint(
                fields=("user", "interest"),
                condition=models.Q(status="ACTIVE"),
                name="unique_active_user_interest",
                violation_error_message="Уже есть активная подписка на интерес.",
            ),
        ),
        migrations.AddConstraint(
            model_name="subscription",
            constraint=models.CheckConstraint(
                condition=models.Q(status__in=[
                    "ACTIVE", "CANCELLED", "COMPLETED"
                ]), name="valid_subscription_status",
            ),
        ),
    ]
