import django.db.models.deletion
from django.db import migrations, models


def link_existing_auto_payments(apps, schema_editor):
    """Attach transactions that older versions created ("Auto-Pay: <name>") to their plan."""
    Subscription = apps.get_model('finance', 'Subscription')
    Transaction = apps.get_model('finance', 'Transaction')
    for sub in Subscription.objects.all():
        Transaction.objects.filter(
            user_id=sub.user_id, recurring__isnull=True, title=f"Auto-Pay: {sub.name}"
        ).update(recurring=sub)


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_subscription_billing_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='transaction_type',
            field=models.CharField(choices=[('INCOME', 'Income'), ('EXPENSE', 'Expense')], default='EXPENSE', max_length=7),
        ),
        migrations.AddField(
            model_name='subscription',
            name='kind',
            field=models.CharField(choices=[('SUBSCRIPTION', 'Subscription'), ('BILL', 'Bill'), ('RENT', 'Rent'), ('SALARY', 'Salary'), ('INSTALLMENT', 'Installment'), ('OTHER', 'Other')], default='SUBSCRIPTION', max_length=12),
        ),
        migrations.AddField(
            model_name='subscription',
            name='category',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='subscription',
            name='total_installments',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='installments_paid',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='recurring',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generated_transactions', to='finance.subscription'),
        ),
        migrations.RunPython(link_existing_auto_payments, migrations.RunPython.noop),
    ]
