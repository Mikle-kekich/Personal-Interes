"""Read-only verification: python docs/pr10/verify_orm.py from project root."""
import os
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interest_tracker.settings")

import django  # noqa: E402

django.setup()

from django.db import connection, transaction  # noqa: E402
from django.db.models import Count, F, Q, Sum  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import CaptureQueriesContext  # noqa: E402

from interests.models import Category, Interest  # noqa: E402
from subscriptions.models import Activity, Subscription  # noqa: E402
from users.models import User  # noqa: E402


print("ПР10: фактическая проверка Django ORM")
print("База:", connection.settings_dict["NAME"])
for model in (Category, User, Interest, Subscription, Activity):
    print(model.__name__, model.objects.count())
print("Статусы:", list(Subscription.objects.values("status").annotate(
    count=Count("pk")
).order_by("status")))
print("Всего часов:", Activity.objects.aggregate(total=Sum("hours")))
print("all / order_by / slice:", list(
    Interest.objects.all().order_by("name").values_list("name", flat=True)[:3]
))
print("filter + Q:", list(Interest.objects.filter(
    Q(weekly_goal__gte=5) | Q(is_active=False)
).values_list("name", flat=True)))
print("exclude:", Interest.objects.exclude(is_active=False).count())
print("get:", Interest.objects.get(pk=1).name)
print("values_list:", list(User.objects.values_list("name", flat=True)))
print("annotate F:", list(Subscription.objects.active().annotate(
    user_name=F("user__name"), interest_name=F("interest__name")
).values("user_name", "interest_name")[:2]))
print("active/cancelled/completed/for_date:",
      Subscription.objects.active().count(),
      Subscription.objects.cancelled().count(),
      Subscription.objects.completed().count(),
      Subscription.objects.for_date("2026-09-08").count())
record = Subscription.objects.first()
with CaptureQueriesContext(connection) as before:
    item = Subscription.objects.get(pk=record.pk)
    _ = (item.user.name, item.interest.category.name)
with CaptureQueriesContext(connection) as after:
    item = Subscription.objects.select_related(
        "user", "interest__category"
    ).get(pk=record.pk)
    _ = (item.user.name, item.interest.category.name)
print("Связанные данные без/с select_related:", len(before), len(after))
print("SQL с JOIN:", after[0]["sql"])
with CaptureQueriesContext(connection) as prefetch:
    for person in User.objects.prefetch_related("subscriptions"):
        _ = list(person.subscriptions.all())
print("Пользователи с коллекцией подписок (prefetch):", len(prefetch))
with transaction.atomic():
    item = Interest.objects.first()
    original_goal = item.weekly_goal
    item.weekly_goal = 6
    item.save(update_fields=["weekly_goal"])
    item.refresh_from_db()
    print("GeneratedField при плане 6:", item.is_intensive)
    item.weekly_goal = 2
    item.save(update_fields=["weekly_goal"])
    item.refresh_from_db()
    print("GeneratedField при плане 2:", item.is_intensive)
    created = User.objects.create(name="Проверка CRUD", email="crud@test.ru")
    created.name = "Проверка UPDATE"
    created.save(update_fields=["name"])
    created.delete()
    print("CRUD create/save/delete: OK; изменения транзакции откатываются")
    transaction.set_rollback(True)
client = Client(HTTP_HOST="localhost")
for url in ("/", "/interests/", "/interests/available/?user=1",
            "/subscriptions/", "/subscriptions/?status=all&page=2",
            "/subscriptions/statistics/", "/subscriptions/1/",
            Interest.objects.get(pk=1).get_absolute_url(),
            "/interests/1/", "/interests/missing/"):
    with CaptureQueriesContext(connection) as captured:
        response = client.get(url)
    print("HTTP", response.status_code, url, "SQL", len(captured))
