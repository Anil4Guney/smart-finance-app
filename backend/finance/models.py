from django.db import models
from django.contrib.auth.models import User

# --- 1. MEVCUT TABLOLAR (Aynen korundu) ---

class Transaction(models.Model):
    """Income or expense transaction."""

    class TransactionType(models.TextChoices):
        INCOME = 'INCOME', 'Income'
        EXPENSE = 'EXPENSE', 'Expense'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default='')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(
        max_length=7,
        choices=TransactionType.choices,
        default=TransactionType.INCOME,
    )
    date = models.DateField()
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Set when the transaction was created automatically by a recurring plan
    recurring = models.ForeignKey(
        'Subscription', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='generated_transactions',
    )

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.title} - {self.transaction_type} {self.amount} ({self.date})"


class SavingsGoal(models.Model):
    """Savings goal with target and current amount."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="savings_goals")
    title = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


# --- 2. YENİ EKLENEN TABLOLAR ---

class CategoryBudget(models.Model):
    """Monthly budget limits for specific categories."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=100)
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'category')

    def __str__(self):
        return f"{self.user.username} - {self.category}: {self.limit_amount}"


class Subscription(models.Model):
    """
    A recurring monthly income or expense: salary, rent, bills, subscriptions
    and installment plans. Due amounts are turned into Transactions
    automatically (see finance/billing.py).
    """

    class Kind(models.TextChoices):
        SUBSCRIPTION = 'SUBSCRIPTION', 'Subscription'
        BILL = 'BILL', 'Bill'
        RENT = 'RENT', 'Rent'
        SALARY = 'SALARY', 'Salary'
        INSTALLMENT = 'INSTALLMENT', 'Installment'
        OTHER = 'OTHER', 'Other'

    # Category used for generated transactions when none is given
    DEFAULT_CATEGORY = {
        Kind.SUBSCRIPTION: 'Bills',
        Kind.BILL: 'Bills',
        Kind.RENT: 'Rent',
        Kind.SALARY: 'Salary',
        Kind.INSTALLMENT: 'Installments',
        Kind.OTHER: 'Other',
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=7,
        choices=Transaction.TransactionType.choices,
        default=Transaction.TransactionType.EXPENSE,
    )
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.SUBSCRIPTION)
    category = models.CharField(max_length=100, blank=True)
    # Installment plans: number of monthly payments in total and how many are done.
    # The plan switches itself off after the last one.
    total_installments = models.PositiveSmallIntegerField(null=True, blank=True)
    installments_paid = models.PositiveSmallIntegerField(default=0)
    # Full price when the user entered the total instead of the monthly amount.
    # The last installment absorbs the rounding difference (6 x 16.67 != 100).
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    # Next payment date. Moved forward one month each time the bill is paid.
    due_date = models.DateField()
    # Day of month the bill is due (1-31). Kept separately so a bill on the 31st
    # returns to the 31st after a short month instead of drifting to the 30th.
    billing_day = models.PositiveSmallIntegerField(null=True, blank=True)

    # --- OTOMATİK ÖDEME İÇİN ALANLAR ---
    auto_pay = models.BooleanField(default=True) # Otomatik işlemlere eklensin mi?
    last_billed_date = models.DateField(null=True, blank=True) # En son otomatik ödeme tarihi
    # ---------------------------------------

    icon = models.CharField(max_length=50, default='pi-credit-card')
    color_class = models.CharField(max_length=100, default='bg-gray-100 text-gray-600')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.name} - {self.amount} (Day: {self.due_date.day})"

    @property
    def effective_category(self):
        return self.category or self.DEFAULT_CATEGORY.get(self.kind, 'Other')

    def payment_amount(self, installment_number=None):
        """Amount of one payment; the last installment settles the exact total price."""
        if (installment_number and self.total_price and self.total_installments
                and installment_number == self.total_installments):
            return self.total_price - self.amount * (self.total_installments - 1)
        return self.amount

    @property
    def remaining_amount(self):
        """Money still to pay on an installment plan (None for ordinary recurring items)."""
        if not self.total_installments:
            return None
        if self.total_price:
            return max(self.total_price - self.amount * self.installments_paid, 0)
        return self.amount * (self.remaining_installments or 0)

    @property
    def remaining_installments(self):
        if not self.total_installments:
            return None
        return max(self.total_installments - self.installments_paid, 0)

    # --- 🗑️ SİLME MANTIĞI: Plan silinince otomatik oluşturduğu işlemleri de siler ---
    def delete(self, *args, **kwargs):
        Transaction.objects.filter(recurring=self).delete()
        # Records created before transactions were linked to their plan
        Transaction.objects.filter(
            user=self.user, recurring__isnull=True, title=f"Auto-Pay: {self.name}"
        ).delete()
        super(Subscription, self).delete(*args, **kwargs)