"""
Subscription auto-billing.

Both the subscriptions API and the `process_subscriptions` management command
use `bill_due_subscriptions`, so a bill is never created twice: each payment
moves the subscription's due_date one month forward inside a locked database
transaction.
"""
import calendar
from datetime import date

from django.db import transaction

from .models import Subscription, Transaction

AUTO_PAY_CATEGORY = 'Bills'


def auto_pay_title(subscription_name: str) -> str:
    return f"Auto-Pay: {subscription_name}"


def next_due_date(current: date, billing_day: int) -> date:
    """Same billing day next month, clamped to the month's last day (31 Jan -> 28/29 Feb -> 31 Mar)."""
    year = current.year + (1 if current.month == 12 else 0)
    month = 1 if current.month == 12 else current.month + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(billing_day, last_day))


def bill_due_subscriptions(user=None, today: date | None = None) -> int:
    """
    Create an expense for every unpaid due date up to `today` and advance due_date.

    Due dates earlier than the day the subscription was added are skipped (moved
    forward without creating an expense), so entering an old start date does not
    flood the user's history. Returns the number of expenses created.
    """
    today = today or date.today()
    due = Subscription.objects.filter(is_active=True, auto_pay=True, due_date__lte=today)
    if user is not None:
        due = due.filter(user=user)

    created = 0
    for sub_id in due.values_list('id', flat=True):
        with transaction.atomic():
            # Lock the row so two simultaneous requests cannot bill the same month twice.
            sub = Subscription.objects.select_for_update().get(pk=sub_id)
            billing_day = sub.billing_day or sub.due_date.day
            added_on = sub.created_at.date() if sub.created_at else sub.due_date

            while sub.is_active and sub.auto_pay and sub.due_date <= today:
                if sub.due_date >= added_on:
                    Transaction.objects.create(
                        user=sub.user,
                        title=auto_pay_title(sub.name),
                        amount=sub.amount,
                        transaction_type=Transaction.TransactionType.EXPENSE,
                        category=AUTO_PAY_CATEGORY,
                        date=sub.due_date,
                        description=f"Automated payment for {sub.name} (Subscription)",
                    )
                    sub.last_billed_date = sub.due_date
                    created += 1
                sub.due_date = next_due_date(sub.due_date, billing_day)

            sub.billing_day = billing_day
            sub.save(update_fields=['due_date', 'billing_day', 'last_billed_date'])
    return created
