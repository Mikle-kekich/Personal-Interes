"""ПР10: веб-сценарии, бизнес-правила, SQL и миграция данных."""
from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from interests.models import Category, Interest
from subscriptions.models import Activity, Subscription
from users.models import User


class ProjectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Спорт")
        cls.user = User.objects.create(name="Иван", email="ivan@example.com")
        cls.other = User.objects.create(name="Анна", email="anna@example.com")
        cls.interest = Interest.objects.create(
            name="Бег", category=cls.category, weekly_goal=4
        )
        cls.second = Interest.objects.create(
            name="Йога", category=cls.category, weekly_goal=6
        )
        cls.record = Subscription.objects.create(
            user=cls.user, interest=cls.interest,
            start_date=date(2026, 9, 14),
        )

    def test_status_managers_and_date(self):
        cancelled = Subscription.objects.create(
            user=self.user, interest=self.second, start_date="2026-09-14",
            status=Subscription.Status.CANCELLED,
        )
        completed = Subscription.objects.create(
            user=self.other, interest=self.second, start_date="2026-09-15",
            status=Subscription.Status.COMPLETED,
        )
        self.assertEqual(list(Subscription.objects.active()), [self.record])
        self.assertEqual(list(Subscription.objects.cancelled()), [cancelled])
        self.assertEqual(list(Subscription.objects.completed()), [completed])
        self.assertEqual(
            Subscription.objects.for_date("2026-09-14").count(), 2
        )

    def test_cancel_keeps_activity_history(self):
        Activity.objects.create(
            subscription=self.record, activity_date="2026-09-14", hours=2
        )
        self.record.cancel()
        self.assertEqual(
            self.record.status, Subscription.Status.CANCELLED
        )
        self.assertEqual(self.record.get_total_hours(), 2)

    def test_active_subscription_blocks_same_user(self):
        self.assertFalse(self.interest.can_subscribe(self.user))
        self.assertTrue(self.interest.can_subscribe(self.other))

    def test_cancelled_and_completed_release_interest(self):
        for status in (Subscription.Status.CANCELLED,
                       Subscription.Status.COMPLETED):
            self.record.status = status
            self.record.save(update_fields=["status"])
            self.assertTrue(self.interest.can_subscribe(self.user))
            response = self.client.get("/interests/available/", {
                "user": self.user.pk, "date": "2026-09-14"
            })
            self.assertIn(self.interest, response.context["interests"])

    def test_available_respects_start_date(self):
        for day, allowed in (("2026-09-13", True), ("2026-09-14", False)):
            response = self.client.get("/interests/available/", {
                "user": self.user.pk, "date": day
            })
            self.assertEqual(
                self.interest in response.context["interests"], allowed
            )

    def test_archived_interest_is_unavailable(self):
        self.second.is_active = False
        self.second.save()
        self.assertFalse(self.second.can_subscribe(self.user))
        record = Subscription(
            user=self.user, interest=self.second, start_date="2026-09-14"
        )
        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_duplicate_active_rejected_by_form_and_database(self):
        record = Subscription(
            user=self.user, interest=self.interest, start_date="2026-09-14"
        )
        with self.assertRaises(ValidationError):
            record.full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            record.save()

    def test_invalid_status_rejected_by_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Subscription.objects.filter(pk=self.record.pk).update(status="BAD")

    def test_slug_transliterated_unique_and_stable(self):
        duplicate = Interest.objects.create(
            name="Бег", category=self.category, weekly_goal=2
        )
        self.assertTrue(duplicate.slug.startswith("beg-"))
        self.assertNotEqual(duplicate.slug, self.interest.slug)
        original = duplicate.get_absolute_url()
        duplicate.name = "Другое название"
        duplicate.save()
        self.assertEqual(duplicate.get_absolute_url(), original)
        self.assertEqual(self.client.get(original).status_code, 200)

    def test_generated_field_recomputed_by_database(self):
        self.assertFalse(self.interest.is_intensive)
        Interest.objects.filter(pk=self.interest.pk).update(weekly_goal=5)
        self.interest.refresh_from_db()
        self.assertTrue(self.interest.is_intensive)
        Interest.objects.filter(pk=self.interest.pk).update(weekly_goal=4.9)
        self.interest.refresh_from_db()
        self.assertFalse(self.interest.is_intensive)

    def test_legacy_url_and_missing_objects(self):
        self.assertEqual(
            self.client.get(f"/interests/{self.interest.pk}/").status_code, 200
        )
        for url in ("/interests/missing/", "/subscriptions/999999/",
                    "/no-such-page/"):
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_search_cyrillic_and_category(self):
        for query in ("БЕГ", "спорт"):
            response = self.client.get("/interests/", {"q": query})
            self.assertIn(self.interest, response.context["interests"])

    def test_status_filter_defaults_to_active(self):
        self.record.cancel()
        response = self.client.get("/subscriptions/")
        self.assertEqual(list(response.context["subscriptions"]), [])
        response = self.client.get("/subscriptions/", {"status": "CANCELLED"})
        self.assertEqual(response.context["page_obj"].paginator.count, 1)
        self.assertContains(response, "отменена")

    def test_filters_sort_and_pagination_preserve_parameters(self):
        for n in range(5):
            user = User.objects.create(name=f"Участник {n}", email="x@test.ru")
            Subscription.objects.create(
                user=user, interest=self.interest, start_date="2026-09-14"
            )
        response = self.client.get("/subscriptions/", {
            "date": "2026-09-14", "interest": self.interest.pk,
            "status": "ACTIVE", "sort": "user", "page": 2,
        })
        page = response.context["page_obj"]
        self.assertEqual(page.number, 2)
        self.assertEqual(page.paginator.count, 6)
        self.assertEqual(len(page), 3)
        self.assertContains(response, "status=ACTIVE")
        self.assertContains(response, f"interest={self.interest.pk}")
        self.assertContains(response, "date=2026-09-14")
        names = [x["user_name"] for x in page]
        self.assertEqual(names, sorted(names))
        response = self.client.get("/subscriptions/", {"user": self.other.pk})
        self.assertEqual(response.context["page_obj"].paginator.count, 0)

    def test_invalid_parameters_do_not_crash(self):
        for url in ("/subscriptions/?date=bad&sort=bad&page=-100",
                    "/subscriptions/?interest=" + "9" * 80,
                    "/interests/available/?user=" + "9" * 80,
                    "/interests/available/?user=1&date=bad"):
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_statistics_all_statuses_and_hours(self):
        Activity.objects.create(
            subscription=self.record, activity_date="2026-09-14", hours=2.5
        )
        Subscription.objects.create(
            user=self.user, interest=self.second, start_date="2026-09-14",
            status=Subscription.Status.COMPLETED,
        )
        self.record.cancel()
        response = self.client.get("/subscriptions/statistics/")
        self.assertEqual(response.context["status_totals"], {
            "active": 0, "cancelled": 1, "completed": 1
        })
        self.assertEqual(response.context["totals"]["total_hours"], 2.5)

    def test_context_processor_used_in_navigation(self):
        response = self.client.get("/")
        self.assertEqual(response.context["catalog_interests_count"], 2)
        self.assertContains(response, "Интересы (2)")
        self.assertContains(response, "Personal-Interes")

    def test_detail_query_count_does_not_grow_with_users(self):
        for n in range(10):
            User.objects.create(name=f"Новый {n}", email="x@test.ru")
        with self.assertNumQueries(4):
            response = self.client.get(self.interest.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_joined_subscription_is_one_query(self):
        with self.assertNumQueries(1):
            item = Subscription.objects.select_related(
                "user", "interest__category"
            ).get(pk=self.record.pk)
            self.assertEqual(item.user.name, "Иван")
            self.assertEqual(item.interest.category.name, "Спорт")

    def test_admin_access_search_filter_and_inlines(self):
        self.assertEqual(self.client.get("/admin/").status_code, 302)
        admin = get_user_model().objects.create_superuser(
            username="testadmin", password="OnlyForTests-2026"
        )
        self.client.force_login(admin)
        for url in ("/admin/", "/admin/interests/interest/",
                    "/admin/subscriptions/activity/",
                    f"/admin/users/user/{self.user.pk}/change/",
                    f"/admin/interests/interest/{self.interest.pk}/change/"):
            self.assertEqual(self.client.get(url).status_code, 200)
        url = reverse("admin:subscriptions_subscription_changelist")
        response = self.client.get(url, {"q": "ivan@example.com"})
        self.assertEqual(response.context["cl"].result_count, 1)
        response = self.client.get(url, {"status__exact": "CANCELLED"})
        self.assertEqual(response.context["cl"].result_count, 0)

    def test_admin_status_change_updates_public_pages(self):
        admin = get_user_model().objects.create_superuser(
            username="testadmin", password="OnlyForTests-2026"
        )
        self.client.force_login(admin)
        response = self.client.post(
            f"/admin/subscriptions/subscription/{self.record.pk}/change/", {
                "user": self.user.pk, "interest": self.interest.pk,
                "start_date": "2026-09-14", "status": "COMPLETED",
                "activities-TOTAL_FORMS": "0",
                "activities-INITIAL_FORMS": "0", "_save": "Сохранить",
            }
        )
        self.assertEqual(response.status_code, 302)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, Subscription.Status.COMPLETED)
        self.assertTrue(self.interest.can_subscribe(self.user))
        response = self.client.get("/subscriptions/")
        self.assertEqual(response.context["page_obj"].paginator.count, 0)


class DataMigrationTests(TransactionTestCase):
    def test_existing_records_preserved_and_transformed(self):
        executor = MigrationExecutor(connection)
        old = [("interests", "0001_initial"),
               ("subscriptions", "0001_initial")]
        latest = executor.loader.graph.leaf_nodes()
        try:
            executor.migrate(old)
            apps = executor.loader.project_state(old).apps
            category = apps.get_model("interests", "Category").objects.create(
                name="Спорт"
            )
            interest = apps.get_model("interests", "Interest").objects.create(
                name="Бег", category=category, weekly_goal=6
            )
            user = apps.get_model("users", "User").objects.create(
                name="Иван", email="x@test.ru"
            )
            model = apps.get_model("subscriptions", "Subscription")
            first = model.objects.create(
                user=user, interest=interest, start_date="2026-09-14"
            )
            second = model.objects.create(
                user=user, interest=interest, start_date="2026-09-14",
                is_cancelled=True,
            )
            executor = MigrationExecutor(connection)
            executor.migrate(latest)
            self.assertEqual(Subscription.objects.get(pk=first.pk).status,
                             Subscription.Status.ACTIVE)
            self.assertEqual(Subscription.objects.get(pk=second.pk).status,
                             Subscription.Status.CANCELLED)
            current = Interest.objects.get(pk=interest.pk)
            self.assertEqual(current.slug, f"beg-{interest.pk}")
            self.assertTrue(current.is_intensive)
        finally:
            MigrationExecutor(connection).migrate(latest)
