from django.core.management.base import BaseCommand

from finance.billing import bill_due_subscriptions


class Command(BaseCommand):
    help = (
        'Günü gelmiş abonelikleri gider olarak kaydeder ve ödeme tarihini 1 ay ileri atar. '
        'Günde bir kez cron ile çalıştırılması önerilir.'
    )

    def handle(self, *args, **kwargs):
        count = bill_due_subscriptions()
        self.stdout.write(self.style.SUCCESS(f'BAŞARILI: {count} adet otomatik ödeme kaydı oluşturuldu.'))
