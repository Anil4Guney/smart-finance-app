import datetime
from django.core.management.base import BaseCommand
from finance.models import Subscription, Transaction

class Command(BaseCommand):
    help = 'Günü gelmiş abonelikleri bulur, gider olarak kaydeder ve tarihi 1 ay ileri atar.'

    def handle(self, *args, **kwargs):
        # 1. Bugünün tarihini al
        today = datetime.date.today()
        
        # 2. Veritabanında aktif olan ve ödeme tarihi bugüne eşit veya geçmiş olan abonelikleri bul
        due_subscriptions = Subscription.objects.filter(is_active=True, due_date__lte=today)
        
        count = 0
        for sub in due_subscriptions:
            # 3. Bu aboneliği kullanıcının harcamalarına (Transactions) OTOMATİK olarak ekle!
            Transaction.objects.create(
                user=sub.user,
                title=f"Auto-payment: {sub.name}",
                amount=sub.amount,
                transaction_type='EXPENSE',
                category='Subscriptions',  # Otomatik "Subscriptions" kategorisine atar
                date=today,
                description='Automated recurring subscription payment.'
            )
            
            # 4. Aboneliğin bir sonraki ödeme tarihini tam 1 ay sonraya hesapla
            month = sub.due_date.month
            year = sub.due_date.year
            
            if month == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month + 1
                next_year = year
                
            # Gün hesaplaması (Örn: 31 Ocak'tan 1 ay sonrası Şubat'ta 31 olmadığı için hata verebilir. Bunu engelliyoruz)
            day = sub.due_date.day
            try:
                next_due_date = datetime.date(next_year, next_month, day)
            except ValueError:
                # Eğer o ay o gün yoksa (Örn: Şubat 30), güvenli olarak o ayın 28'ine at.
                next_due_date = datetime.date(next_year, next_month, 28)
                
            # 5. Yeni tarihi kaydet
            sub.due_date = next_due_date
            sub.save()
            
            count += 1
            
        # 6. Terminale bilgi mesajı yazdır
        self.stdout.write(self.style.SUCCESS(f'BAŞARILI: Toplam {count} adet abonelik otomatik olarak ödendi ve güncellendi!'))