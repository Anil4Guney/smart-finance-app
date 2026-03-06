import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User

from finance.models import Transaction, SavingsGoal


class Command(BaseCommand):
    help = "Seed the database with sample Transactions and SavingsGoals for a user."

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='testuser',
            help='Username to create seed data for (default: testuser)',
        )

    def handle(self, *args, **options):
        username = options['username']
        
        # Get or create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))

        self.stdout.write(f"Clearing existing finance data for user: {username}...")
        Transaction.objects.filter(user=user).delete()
        SavingsGoal.objects.filter(user=user).delete()

        today = timezone.now().date()

        # Sample categories and titles
        income_categories = ["Salary", "Bonus"]
        expense_categories = ["Food", "Rent", "Entertainment"]

        self.stdout.write("Creating sample transactions...")
        for i in range(5):
            is_income = random.choice([True, False])
            if is_income:
                transaction_type = Transaction.TransactionType.INCOME
                category = random.choice(income_categories)
                title = f"{category} Income"
                amount = random.randint(1000, 5000)
            else:
                transaction_type = Transaction.TransactionType.EXPENSE
                category = random.choice(expense_categories)
                title = f"{category} Expense"
                amount = random.randint(50, 1500)

            Transaction.objects.create(
                user=user,
                title=title,
                amount=amount,
                transaction_type=transaction_type,
                date=today - timedelta(days=random.randint(0, 30)),
                category=category,
                description="Seeded sample transaction",
            )

        self.stdout.write("Creating sample savings goals...")
        SavingsGoal.objects.create(
            user=user,
            name="New Mac",
            target_amount=3000,
            current_amount=750,
        )
        SavingsGoal.objects.create(
            user=user,
            name="Vacation",
            target_amount=2000,
            current_amount=500,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Database seeded with sample finance data for user: {username}"
            )
        )

