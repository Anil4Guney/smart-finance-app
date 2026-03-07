from django.db import models
from django.contrib.auth.models import User

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
        # Hedefleri en son eklenene göre sıralar
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"