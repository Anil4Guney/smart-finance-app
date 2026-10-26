from django.contrib import admin

from .models import CategoryBudget, SavingsGoal, Subscription, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'amount', 'transaction_type', 'category', 'date')
    list_filter = ('transaction_type', 'category', 'date')
    search_fields = ('title', 'description', 'category', 'user__username')
    raw_id_fields = ('user', 'recurring')


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'target_amount', 'current_amount')
    search_fields = ('title', 'user__username')
    raw_id_fields = ('user',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'kind', 'transaction_type', 'amount', 'due_date', 'is_active', 'auto_pay')
    list_filter = ('kind', 'transaction_type', 'is_active', 'auto_pay')
    search_fields = ('name', 'user__username')
    raw_id_fields = ('user',)


@admin.register(CategoryBudget)
class CategoryBudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'user', 'limit_amount')
    search_fields = ('category', 'user__username')
    raw_id_fields = ('user',)
