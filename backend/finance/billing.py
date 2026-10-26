"""
Recurring income/expense processing (salary, rent, bills, subscriptions, installments).

Both the recurring-plans API and the `process_subscriptions` management command
use `bill_due_subscriptions`, so a payment is never created twice: each one
moves the plan's due_date one month forward inside a locked database transaction.
"""
import calendar
from datetime import date

from django.db import transaction

from .models import Subscription, Transaction


def auto_pay_title(sub: Subscription, installment_number: int | None = None) -> str:
    if installment_number and sub.total_installments:
        return f"{sub.name} ({installment_number}/{sub.total_installments})"
    return sub.name


def next_due_date(current: date, billing_day: int) -> date:
    """Same billing day next month, clamped to the month's last day (31 Jan -> 28/29 Feb -> 31 Mar)."""
    year = current.year + (1 if current.month == 12 else 0)
    month = 1 if current.month == 12 else current.month + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(billing_day, last_day))


def _installments_left(sub: Subscription) -> bool:
    return not sub.total_installments or sub.installments_paid < sub.total_installments


def bill_due_subscriptions(user=None, today: date | None = None) -> int:
    """
    Create a transaction for every unpaid due date up to `today` and advance due_date.

    Due dates earlier than the day the plan was added are skipped (moved forward
    without creating a transaction), so entering an old start date does not flood
    the user's history. Installment plans stop after their last payment.
    Returns the number of transactions created.
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

            while sub.is_active and sub.auto_pay and sub.due_date <= today and _installments_left(sub):
                if sub.due_date >= added_on:
                    number = sub.installments_paid + 1 if sub.total_installments else None
                    is_income = sub.transaction_type == Transaction.TransactionType.INCOME
                    Transaction.objects.create(
                        user=sub.user,
                        recurring=sub,
                        title=auto_pay_title(sub, number),
                        amount=sub.amount,
                        transaction_type=sub.transaction_type,
                        category=sub.effective_category,
                        date=sub.due_date,
                        description=f"Automatic {'income' if is_income else 'payment'}: {sub.name} (recurring)",
                    )
                    sub.last_billed_date = sub.due_date
                    if sub.total_installments:
                        sub.installments_paid += 1
                    created += 1
                elif sub.total_installments:
                    # A skipped past installment still counts as paid before the app knew about it
                    sub.installments_paid += 1
                sub.due_date = next_due_date(sub.due_date, billing_day)

            if not _installments_left(sub):
                sub.is_active = False  # last installment done
            sub.billing_day = billing_day
            sub.save(update_fields=['due_date', 'billing_day', 'last_billed_date', 'installments_paid', 'is_active'])
    return created
