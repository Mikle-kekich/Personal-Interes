from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("interests", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="interest", name="slug",
            field=models.SlugField(
                max_length=180, null=True, editable=False,
                verbose_name="URL-идентификатор",
            ),
        ),
        migrations.AddField(
            model_name="interest", name="is_intensive",
            field=models.GeneratedField(
                expression=models.Case(
                    models.When(weekly_goal__gte=5, then=models.Value(True)),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                ), output_field=models.BooleanField(), db_persist=True,
                verbose_name="Интенсивный план от 5 ч",
            ),
        ),
    ]
