from django.db import migrations


def forwards(apps, schema_editor):
    subscription = apps.get_model("subscriptions", "Subscription")
    records = subscription.objects.using(schema_editor.connection.alias)
    records.filter(is_cancelled=True).update(status="CANCELLED")
    records.filter(is_cancelled=False).update(status="ACTIVE")


def backwards(apps, schema_editor):
    subscription = apps.get_model("subscriptions", "Subscription")
    records = subscription.objects.using(schema_editor.connection.alias)
    records.update(is_cancelled=False)
    records.filter(status="CANCELLED").update(is_cancelled=True)


class Migration(migrations.Migration):
    dependencies = [("subscriptions", "0002_subscription_status")]
    operations = [migrations.RunPython(forwards, backwards)]
