from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def populate_slugs(apps, schema_editor):
    interest = apps.get_model("interests", "Interest")
    for item in interest.objects.using(
        schema_editor.connection.alias
    ).order_by("pk").iterator():
        base = slugify(unidecode(item.name))[:140] or "interest"
        item.slug = f"{base}-{item.pk}"
        item.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("interests", "0002_slug_and_generated_field")]
    operations = [migrations.RunPython(
        populate_slugs, migrations.RunPython.noop
    )]
