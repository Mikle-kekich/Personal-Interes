from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("interests", "0003_populate_slugs")]
    operations = [migrations.AlterField(
        model_name="interest", name="slug",
        field=models.SlugField(
            max_length=180, unique=True, editable=False,
            verbose_name="URL-идентификатор",
        ),
    )]
