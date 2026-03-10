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
    """Recurring bills and subscriptions with auto-billing logic."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField() # Başlangıç/Sıradaki ödeme günü
    
    # --- OTOMATİK ÖDEME İÇİN ALANLAR ---
    auto_pay = models.BooleanField(default=True) # Otomatik işlemlere eklensin mi?
    last_billed_date = models.DateField(null=True, blank=True) # En son hangi ayın faturası kesildi?
    # ---------------------------------------

    icon = models.CharField(max_length=50, default='pi-credit-card')
    color_class = models.CharField(max_length=100, default='bg-gray-100 text-gray-600')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.name} - {self.amount} (Day: {self.due_date.day})"

    # --- 🗑️ SİLME MANTIĞI: Abonelik silinince Transactions'taki Auto-Pay kayıtlarını da siler ---
    def delete(self, *args, **kwargs):
        Transaction.objects.filter(
            user=self.user, 
            title=f"Auto-Pay: {self.name}"
        ).delete()
        super(Subscription, self).delete(*args, **kwargs)