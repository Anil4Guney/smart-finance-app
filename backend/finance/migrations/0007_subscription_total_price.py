from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_recurring_income_expense'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
