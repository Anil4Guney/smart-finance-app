from django.db import migrations, models


def fill_billing_day(apps, schema_editor):
    Subscription = apps.get_model('finance', 'Subscription')
    for sub in Subscription.objects.filter(billing_day__isnull=True):
        sub.billing_day = sub.due_date.day
        sub.save(update_fields=['billing_day'])


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_subscription_auto_pay_subscription_last_billed_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='billing_day',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(fill_billing_day, migrations.RunPython.noop),
    ]
