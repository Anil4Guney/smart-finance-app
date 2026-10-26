"""
Month-end forecast: where the user's balance for this month is heading.

    projected income  = income recorded this month + recurring income still to come
    projected expense = expenses recorded this month + recurring expenses still to come
                        + expected everyday (non-recurring) spending for the rest of the month

Everyday spending is estimated from the daily pace this month, blended with the
last 90 days early in the month when this month has too little data.
All amounts are in the stored base currency (USD).
"""
import calendar
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum

from .billing import next_due_date
from .models import Subscription, Transaction

HISTORY_DAYS = 90
TWO_PLACES = Decimal('0.01')


def _sum(qs) -> Decimal:
    return qs.aggregate(total=Sum('amount'))['total'] or Decimal('0')


def _money(value: Decimal) -> float:
    return float(Decimal(value).quantize(TWO_PLACES))


def _upcoming_occurrences(sub: Subscription, after: date, until: date) -> list[date]:
    """Payment dates of `sub` in (after, until]."""
    billing_day = sub.billing_day or sub.due_date.day
    if sub.auto_pay:
        current = sub.due_date  # next unpaid date (past ones were billed already)
    else:
        # Manual plans don't move due_date forward; start from this month's billing day
        last = calendar.monthrange(after.year, after.month)[1]
        current = max(sub.due_date, date(after.year, after.month, min(billing_day, last)))
    remaining = sub.remaining_installments
    dates = []
    while current <= until and (remaining is None or len(dates) < remaining):
        if current > after:
            dates.append(current)
        current = next_due_date(current, billing_day)
    return dates


def monthly_forecast(user, today: date | None = None) -> dict:
    today = today or date.today()
    month_start = today.replace(day=1)
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    month_end = today.replace(day=days_in_month)
    days_left = days_in_month - today.day

    month_tx = Transaction.objects.filter(user=user, date__gte=month_start, date__lte=month_end)
    income_so_far = _sum(month_tx.filter(transaction_type='INCOME'))
    expense_so_far = _sum(month_tx.filter(transaction_type='EXPENSE'))

    # --- Recurring income/expenses still to come this month ---
    upcoming = []
    upcoming_income = upcoming_expense = Decimal('0')
    for sub in Subscription.objects.filter(user=user, is_active=True):
        for when in _upcoming_occurrences(sub, today, month_end):
            upcoming.append({
                'id': sub.id,
                'name': sub.name,
                'kind': sub.kind,
                'transaction_type': sub.transaction_type,
                'amount': _money(sub.amount),
                'date': when.isoformat(),
            })
            if sub.transaction_type == 'INCOME':
                upcoming_income += sub.amount
            else:
                upcoming_expense += sub.amount
    upcoming.sort(key=lambda item: item['date'])

    # --- Everyday (non-recurring) spending pace ---
    variable = Transaction.objects.filter(user=user, transaction_type='EXPENSE', recurring__isnull=True)
    variable_so_far = _sum(variable.filter(date__gte=month_start, date__lte=today))
    current_rate = variable_so_far / today.day

    history_start = month_start - timedelta(days=HISTORY_DAYS)
    first_tx = Transaction.objects.filter(user=user).order_by('date').values_list('date', flat=True).first()
    history_rate = None
    if first_tx and first_tx < month_start:
        history_days = (month_start - max(first_tx, history_start)).days
        history_total = _sum(variable.filter(date__gte=history_start, date__lt=month_start))
        history_rate = history_total / history_days

    if history_rate is None:
        daily_rate, method = current_rate, 'this_month'
    else:
        # Trust this month more as it progresses
        weight = Decimal(today.day) / Decimal(days_in_month)
        daily_rate = weight * current_rate + (1 - weight) * history_rate
        method = 'blended'
    expected_variable = daily_rate * days_left

    projected_income = income_so_far + upcoming_income
    projected_expense = expense_so_far + upcoming_expense + expected_variable

    # What can be spent per day (today included) without ending the month negative
    free_money = income_so_far + upcoming_income - expense_so_far - upcoming_expense
    safe_daily = max(free_money, Decimal('0')) / (days_left + 1)

    return {
        'month': month_start.strftime('%Y-%m'),
        'today': today.isoformat(),
        'days_left': days_left,
        'income_so_far': _money(income_so_far),
        'expense_so_far': _money(expense_so_far),
        'upcoming_income': _money(upcoming_income),
        'upcoming_expense': _money(upcoming_expense),
        'expected_variable_spending': _money(expected_variable),
        'daily_spending_rate': _money(daily_rate),
        'projected_income': _money(projected_income),
        'projected_expense': _money(projected_expense),
        'projected_net': _money(projected_income - projected_expense),
        'safe_daily_spend': _money(safe_daily),
        'has_recurring_income': Subscription.objects.filter(
            user=user, is_active=True, transaction_type='INCOME'
        ).exists(),
        'method': method,
        'upcoming': upcoming,
    }
