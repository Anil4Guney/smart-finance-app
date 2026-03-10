import os
import google.generativeai as genai
from django.conf import settings
from datetime import date # Tarih kontrolü için eklendi

from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# 1. TÜM MODELLERİ VE SERIALIZER'LARI İÇERİ AKTARIYORUZ
from .models import Transaction, SavingsGoal, CategoryBudget, Subscription
from .serializers import (
    TransactionSerializer, 
    SavingsGoalSerializer, 
    CategoryBudgetSerializer, 
    SubscriptionSerializer
)
from .services import analyze_receipt

# --- MEVCUT VİEWSET'LER (Aynen Korundu) ---

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavingsGoalViewSet(viewsets.ModelViewSet):
    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryBudgetViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryBudgetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return CategoryBudget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --- 🚀 GÜNCELLENEN VİEWSET: OTOMATİK ÖDEME MANTIĞI EKLENDİ ---

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        today = date.today()
        
        # Kullanıcının aktif ve otomatik ödemesi açık olan aboneliklerini çek
        subscriptions = Subscription.objects.filter(user=user, is_active=True, auto_pay=True)

        for sub in subscriptions:
            # Kontrol: Ödeme günü geldi mi (veya geçti mi) VE bu ay henüz fatura kesilmedi mi?
            is_due = today.day >= sub.due_date.day
            has_not_billed_this_month = (
                sub.last_billed_date is None or 
                (sub.last_billed_date.month != today.month or sub.last_billed_date.year != today.year)
            )

            if is_due and has_not_billed_this_month:
                # Otomatik harcama kaydı oluştur
                Transaction.objects.create(
                    user=user,
                    title=f"Auto-Pay: {sub.name}",
                    amount=sub.amount,
                    transaction_type='EXPENSE',
                    category='Bills',
                    date=today,
                    description=f"Automated payment for {sub.name} (Subscription)"
                )

                # Aboneliği güncelle (Bu ay ödendi olarak işaretle)
                sub.last_billed_date = today
                sub.save()

        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --- FİŞ TARAMA (Aynen Korundu) ---

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def scan_receipt(request: Request) -> Response:
    """Accept an image file, run AI receipt analysis, return extracted JSON."""
    image = request.FILES.get("image") or request.FILES.get("file")
    if not image:
        return Response(
            {"detail": "No image file provided. Send a multipart field named 'image' or 'file'."},
            status=400,
        )
    try:
        data = analyze_receipt(image)
        return Response(data)
    except ValueError as e:
        return Response({"detail": str(e)}, status=500)
    except Exception as e:
        return Response({"detail": f"Receipt analysis failed: {str(e)}"}, status=500)


# --- SENİN ORİJİNAL PROMPT'LARINLA YAPAY ZEKA SOHBET ASİSTANI ---

class AIChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Frontend'den gelen sohbet mesajını alır, kullanıcının finansal verileriyle harmanlar ve Gemini'a sorar."""
        user_message = request.data.get('prompt')
        
        if not user_message:
            return Response({"error": "Prompt is required"}, status=400)

        user = request.user
        
        # Kullanıcının tüm finansal bağlamını (Context) veritabanından çekiyoruz
        transactions = Transaction.objects.filter(user=user)
        budgets = CategoryBudget.objects.filter(user=user)
        subscriptions = Subscription.objects.filter(user=user)

        total_income = sum(float(t.amount) for t in transactions if t.transaction_type == 'INCOME')
        total_expense = sum(float(t.amount) for t in transactions if t.transaction_type == 'EXPENSE')

        # Yapay zekaya göndermek için verileri kısa özet metinlere çeviriyoruz
        tx_details = ", ".join([f"{t.category}: ${t.amount}" for t in transactions[:15]])
        budget_details = ", ".join([f"{b.category}: ${b.limit_amount}" for b in budgets])
        sub_details = ", ".join([f"{s.name}: ${s.amount}" for s in subscriptions])

        # SENİN ORİJİNAL SİSTEM PROMPT'UN
        system_prompt = f"""
        Sen 'SmartFinance' uygulaması için çalışan uzman, samimi ve zeki bir finansal yapay zeka asistanısın.
        Kullanıcının adı: {user.first_name or user.username}.

        Kullanıcının Güncel Finansal Durumu:
        - Toplam Gelir: ${total_income}
        - Toplam Gider: ${total_expense}
        - Son Harcamaları: {tx_details if tx_details else 'Henüz harcama yok'}
        - Belirlediği Bütçe Limitleri: {budget_details if budget_details else 'Henüz limit yok'}
        - Yaklaşan Abonelikleri: {sub_details if sub_details else 'Abonelik yok'}

        Kullanıcı sana aşağıdaki soruyu sordu. 
        If her question is about her own expenses, budgets or subscriptions, answer clearly and correctly using the data above. 
        Eğer genel bir finans/yatırım sorusuysa, güncel bilgilere dayanarak profesyonel bir tavsiye ver. 
        Konuşma dilin doğal, okuması kolay olsun ve uygun yerlerde emoji kullan.
        ASLA JSON formatı döndürme, sadece normal sohbet metni (Markdown destekli) döndür.

        Kullanıcının Sorusu: "{user_message}"
        """

        try:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                return Response({"error": "API Key .env dosyasından okunamadı!"}, status=400)

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash') # En güncel model
            
            # Gemini'a promptu gönderiyoruz
            response = model.generate_content(system_prompt)
            
            # Frontend'e "reply" objesi içinde düz metin dönüyoruz
            return Response({"reply": response.text})
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)