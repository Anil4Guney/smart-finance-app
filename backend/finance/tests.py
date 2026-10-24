from io import StringIO
from datetime import date, datetime, timezone
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from .billing import bill_due_subscriptions, next_due_date
from .models import CategoryBudget, Subscription, Transaction


def make_subscription(user, due, created=date(2026, 1, 1), **extra):
    sub = Subscription.objects.create(
        user=user, name='Netflix', amount=Decimal('9.99'), due_date=due,
        billing_day=extra.pop('billing_day', due.day), **extra,
    )
    # created_at is auto_now_add; set it explicitly for predictable tests
    Subscription.objects.filter(pk=sub.pk).update(
        created_at=datetime(created.year, created.month, created.day, tzinfo=timezone.utc)
    )
    sub.refresh_from_db()
    return sub


class NextDueDateTests(TestCase):
    def test_regular_month(self):
        self.assertEqual(next_due_date(date(2026, 3, 15), 15), date(2026, 4, 15))

    def test_year_rollover(self):
        self.assertEqual(next_due_date(date(2026, 12, 5), 5), date(2027, 1, 5))

    def test_short_month_clamps_and_recovers(self):
        feb = next_due_date(date(2026, 1, 31), 31)
        self.assertEqual(feb, date(2026, 2, 28))
        self.assertEqual(next_due_date(feb, 31), date(2026, 3, 31))


class BillingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ali', password='S3cure-pass-123')

    def test_bills_once_and_advances_due_date(self):
        sub = make_subscription(self.user, date(2026, 3, 10))
        self.assertEqual(bill_due_subscriptions(today=date(2026, 3, 12)), 1)
        # Running again (API + cron) must not bill the same month twice
        self.assertEqual(bill_due_subscriptions(today=date(2026, 3, 12)), 0)

        sub.refresh_from_db()
        self.assertEqual(sub.due_date, date(2026, 4, 10))
        self.assertEqual(sub.last_billed_date, date(2026, 3, 10))
        tx = Transaction.objects.get(user=self.user)
        self.assertEqual(tx.title, 'Auto-Pay: Netflix')
        self.assertEqual(tx.date, date(2026, 3, 10))
        self.assertEqual(tx.transaction_type, 'EXPENSE')

    def test_not_due_yet(self):
        make_subscription(self.user, date(2026, 3, 20))
        self.assertEqual(bill_due_subscriptions(today=date(2026, 3, 12)), 0)

    def test_catches_up_missed_months(self):
        make_subscription(self.user, date(2026, 1, 31))
        self.assertEqual(bill_due_subscriptions(today=date(2026, 3, 31)), 3)
        dates = sorted(Transaction.objects.values_list('date', flat=True))
        self.assertEqual(dates, [date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31)])

    def test_skips_dates_before_subscription_was_added(self):
        sub = make_subscription(self.user, date(2025, 6, 5), created=date(2026, 3, 1))
        self.assertEqual(bill_due_subscriptions(today=date(2026, 3, 10)), 1)
        self.assertEqual(Transaction.objects.get().date, date(2026, 3, 5))
        sub.refresh_from_db()
        self.assertEqual(sub.due_date, date(2026, 4, 5))

    def test_inactive_or_manual_subscriptions_are_ignored(self):
        make_subscription(self.user, date(2026, 3, 1), is_active=False)
        make_subscription(self.user, date(2026, 3, 1), auto_pay=False)
        self.assertEqual(bill_due_subscriptions(today=date(2026, 3, 10)), 0)

    def test_only_given_user_is_billed(self):
        other = User.objects.create_user('ayse', password='S3cure-pass-123')
        make_subscription(self.user, date(2026, 3, 1))
        make_subscription(other, date(2026, 3, 1))
        self.assertEqual(bill_due_subscriptions(user=self.user, today=date(2026, 3, 10)), 1)
        self.assertFalse(Transaction.objects.filter(user=other).exists())

    def test_management_command_uses_same_logic(self):
        make_subscription(self.user, date(2020, 1, 1), created=date(2019, 12, 1))
        call_command('process_subscriptions', stdout=StringIO())
        count = Transaction.objects.count()
        self.assertGreater(count, 0)
        call_command('process_subscriptions', stdout=StringIO())
        self.assertEqual(Transaction.objects.count(), count)


class ApiTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user('ali', password='S3cure-pass-123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)


class BudgetApiTests(ApiTestCase):
    def test_sync_creates_updates_and_removes(self):
        res = self.client.put('/api/budgets/sync/', {'limits': {'Food': 300, 'Rent': 1000}}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual({b['category'] for b in res.data}, {'Food', 'Rent'})

        res = self.client.put('/api/budgets/sync/', {'limits': {'Food': 250.5, 'Rent': None}}, format='json')
        self.assertEqual(res.status_code, 200)
        budgets = CategoryBudget.objects.filter(user=self.user)
        self.assertEqual(budgets.count(), 1)
        self.assertEqual(budgets.get().limit_amount, Decimal('250.50'))

    def test_sync_rejects_bad_input(self):
        self.assertEqual(self.client.put('/api/budgets/sync/', {'limits': 'x'}, format='json').status_code, 400)
        self.assertEqual(self.client.put('/api/budgets/sync/', {'limits': {'Food': 'abc'}}, format='json').status_code, 400)
        self.assertEqual(self.client.put('/api/budgets/sync/', {'limits': {'Food': -5}}, format='json').status_code, 400)

    def test_users_only_see_their_own_budgets(self):
        other = User.objects.create_user('ayse', password='S3cure-pass-123')
        CategoryBudget.objects.create(user=other, category='Food', limit_amount=50)
        res = self.client.get('/api/budgets/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, [])

    def test_requires_login(self):
        self.assertEqual(APIClient().get('/api/budgets/').status_code, 401)


class SubscriptionApiTests(ApiTestCase):
    def test_create_sets_billing_day_and_update_follows_due_date(self):
        res = self.client.post('/api/subscriptions/', {
            'name': 'Spotify', 'amount': '5.99', 'due_date': '2099-01-31',
        }, format='json')
        self.assertEqual(res.status_code, 201)
        sub = Subscription.objects.get(pk=res.data['id'])
        self.assertEqual(sub.billing_day, 31)

        self.client.patch(f'/api/subscriptions/{sub.pk}/', {'due_date': '2099-02-14'}, format='json')
        sub.refresh_from_db()
        self.assertEqual(sub.billing_day, 14)

    def test_listing_bills_due_subscriptions_once(self):
        make_subscription(self.user, date.today(), created=date.today())
        self.client.get('/api/subscriptions/')
        self.client.get('/api/subscriptions/')
        self.assertEqual(Transaction.objects.filter(user=self.user).count(), 1)


class PasswordChangeTests(TestCase):
    def test_set_password_endpoint_changes_password(self):
        user = User.objects.create_user('ali', password='S3cure-pass-123')
        client = APIClient()
        client.force_authenticate(user)

        bad = client.post('/auth/users/set_password/', {
            'current_password': 'wrong', 'new_password': 'An0ther-pass-456',
        }, format='json')
        self.assertEqual(bad.status_code, 400)
        self.assertIn('current_password', bad.data)

        ok = client.post('/auth/users/set_password/', {
            'current_password': 'S3cure-pass-123', 'new_password': 'An0ther-pass-456',
        }, format='json')
        self.assertEqual(ok.status_code, 204)
        user.refresh_from_db()
        self.assertTrue(user.check_password('An0ther-pass-456'))


class AiEndpointLimitsTests(ApiTestCase):
    def test_receipt_too_large_is_rejected(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings

        with override_settings(MAX_RECEIPT_UPLOAD_BYTES=10):
            image = SimpleUploadedFile('r.jpg', b'x' * 20, content_type='image/jpeg')
            res = self.client.post('/api/scan-receipt/', {'image': image}, format='multipart')
        self.assertEqual(res.status_code, 400)

    def test_chat_is_rate_limited(self):
        from rest_framework.settings import api_settings
        from .views import AIChatThrottle

        original = AIChatThrottle.THROTTLE_RATES
        AIChatThrottle.THROTTLE_RATES = {**api_settings.DEFAULT_THROTTLE_RATES, 'ai_chat': '2/hour'}
        try:
            codes = [self.client.post('/api/chat/', {'prompt': ''}, format='json').status_code for _ in range(3)]
        finally:
            AIChatThrottle.THROTTLE_RATES = original
        self.assertEqual(codes, [400, 400, 429])
