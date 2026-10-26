import logging
from decimal import Decimal, InvalidOperation

import google.generativeai as genai
from django.conf import settings
from django.db import transaction as db_transaction

from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle
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
from .services import analyze_receipt, describe_ai_error
from .billing import bill_due_subscriptions
from .forecast import monthly_forecast

logger = logging.getLogger(__name__)


class AIChatThrottle(UserRateThrottle):
    scope = 'ai_chat'


class ReceiptScanThrottle(UserRateThrottle):
    scope = 'receipt_scan'

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

    @action(detail=False, methods=['put'], url_path='sync')
    def sync(self, request):
        """
        Save all category limits at once.
        Body: {"limits": {"Food": 300, "Rent": null}} -- a number sets the limit,
        null/0 removes it. Categories not in the body are left unchanged.
        """
        limits = request.data.get('limits')
        if not isinstance(limits, dict):
            return Response({'detail': '"limits" must be an object of {category: amount}.'}, status=400)

        cleaned = {}
        for category, raw in limits.items():
            category = str(category).strip()[:100]
            if not category:
                continue
            if raw in (None, '', 0):
                cleaned[category] = None
                continue
            try:
                amount = Decimal(str(raw)).quantize(Decimal('0.01'))
            except (InvalidOperation, ValueError):
                return Response({'detail': f'Invalid amount for {category}.'}, status=400)
            if amount < 0 or amount >= Decimal('10000000000'):
                return Response({'detail': f'Amount out of range for {category}.'}, status=400)
            cleaned[category] = amount if amount > 0 else None

        with db_transaction.atomic():
            for category, amount in cleaned.items():
                if amount is None:
                    CategoryBudget.objects.filter(user=request.user, category=category).delete()
                else:
                    CategoryBudget.objects.update_or_create(
                        user=request.user, category=category, defaults={'limit_amount': amount}
                    )

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


# --- ABONELİKLER: otomatik ödeme mantığı finance/billing.py içinde ---

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Hosts without a scheduler (e.g. Render free tier) never run the cron
        # command, so due bills are also processed when the user opens the list.
        # Safe to run repeatedly: each bill moves due_date forward under a row lock.
        bill_due_subscriptions(user=request.user)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --- FİŞ TARAMA (Aynen Korundu) ---

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@throttle_classes([ReceiptScanThrottle])
def scan_receipt(request: Request) -> Response:
    """Accept an image file, run AI receipt analysis, return extracted JSON."""
    image = request.FILES.get("image") or request.FILES.get("file")
    if not image:
        return Response(
            {"detail": "No image file provided. Send a multipart field named 'image' or 'file'."},
            status=400,
        )
    if image.size > settings.MAX_RECEIPT_UPLOAD_BYTES:
        max_mb = settings.MAX_RECEIPT_UPLOAD_BYTES // (1024 * 1024)
        return Response({"detail": f"Image is too large (max {max_mb} MB)."}, status=400)
    try:
        data = analyze_receipt(image)
        return Response(data)
    except Exception as exc:
        logger.exception("Receipt analysis failed")
        status_code, message = describe_ai_error(exc, fallback="Receipt analysis failed. Please try another photo.")
        return Response({"detail": message}, status=status_code)


# --- SENİN ORİJİNAL PROMPT'LARINLA YAPAY ZEKA SOHBET ASİSTANI ---

class AIChatView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIChatThrottle]

    def post(self, request):
        """Frontend'den gelen sohbet mesajını alır, kullanıcının finansal verileriyle harmanlar ve Gemini'a sorar."""
        user_message = request.data.get('prompt')
        
        if not user_message or not str(user_message).strip():
            return Response({"error": "Prompt is required"}, status=400)
        user_message = str(user_message)[:2000]

        user = request.user
        
        # Kullanıcının tüm finansal bağlamını (Context) veritabanından çekiyoruz
        transactions = Transaction.objects.filter(user=user)
        budgets = CategoryBudget.objects.filter(user=user)
        subscriptions = Subscription.objects.filter(user=user, is_active=True)
        forecast = monthly_forecast(user)

        total_income = sum(float(t.amount) for t in transactions if t.transaction_type == 'INCOME')
        total_expense = sum(float(t.amount) for t in transactions if t.transaction_type == 'EXPENSE')

        # Yapay zekaya göndermek için verileri tarihli, kısa özet metinlere çeviriyoruz
        def sign(tx_type):
            return "+" if tx_type == "INCOME" else "-"

        tx_details = "; ".join(
            f"{t.date:%d.%m.%Y} {t.title} ({t.category}): {sign(t.transaction_type)}${t.amount}"
            for t in transactions[:15]
        )
        budget_details = ", ".join([f"{b.category}: ${b.limit_amount}" for b in budgets])

        def describe(s):
            extra = f", {s.remaining_installments} taksit kaldı" if s.total_installments else ""
            return (f"{s.name} ({s.get_kind_display()}): {sign(s.transaction_type)}${s.amount} her ay, "
                    f"sonraki tarih {s.due_date:%d.%m.%Y}{extra}")
        sub_details = "; ".join(describe(s) for s in subscriptions)

        # SENİN ORİJİNAL SİSTEM PROMPT'UN
        system_prompt = f"""
        Sen 'SmartFinance' uygulaması için çalışan uzman, samimi ve zeki bir finansal yapay zeka asistanısın.
        Kullanıcının adı: {user.first_name or user.username}.

        Bugünün tarihi: {forecast['today']}. Tüm tutarlar USD cinsindendir.

        Kullanıcının Güncel Finansal Durumu:
        - Bu ay şimdiye kadar: gelir ${forecast['income_so_far']}, gider ${forecast['expense_so_far']}
        - Tüm zamanların toplamı: gelir ${total_income}, gider ${total_expense}
        - Son İşlemleri (tarihli): {tx_details if tx_details else 'Henüz işlem yok'}
        - Belirlediği Bütçe Limitleri: {budget_details if budget_details else 'Henüz limit yok'}
        - Her Ay Tekrarlayan Gelir/Giderleri: {sub_details if sub_details else 'Tanımlı değil'}
        - Bu Ayın Sonu Tahmini (sadece bu ayın tarihlerini kapsar): tahmini gelir ${forecast['projected_income']}, tahmini gider ${forecast['projected_expense']}, ay sonu net ${forecast['projected_net']}, ay sonuna {forecast['days_left']} gün var, günlük güvenli harcama ${forecast['safe_daily_spend']}

        Kullanıcı sana aşağıdaki soruyu sordu. 
        Soru kendi harcamaları, bütçeleri veya abonelikleriyle ilgiliyse yukarıdaki verileri kullanarak net ve doğru cevap ver.
        Tarihlere dikkat et: başka aya ait işlemleri bu ayın harcaması gibi gösterme, sonraki tarihi bu aydan sonra olan gelirleri bu aya sayma.
        Eğer genel bir finans/yatırım sorusuysa, güncel bilgilere dayanarak profesyonel bir tavsiye ver. 
        Konuşma dilin doğal, okuması kolay olsun ve uygun yerlerde emoji kullan.
        ASLA JSON formatı döndürme. Markdown kullanma (yıldız, diyez yok); düz metin ve gerekirse "- " ile başlayan maddeler yaz.
        Kullanıcı hangi dilde sorduysa o dilde cevap ver.

        Kullanıcının Sorusu: "{user_message}"
        """

        try:
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                return Response({"error": "AI service is not configured."}, status=503)

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
            
            # Gemini'a promptu gönderiyoruz
            response = model.generate_content(
                system_prompt, request_options={'timeout': settings.AI_CHAT_TIMEOUT_SECONDS}
            )
            
            # Frontend'e "reply" objesi içinde düz metin dönüyoruz
            return Response({"reply": response.text})
            
        except Exception as exc:
            logger.exception("AI chat request failed")
            status_code, message = describe_ai_error(exc)
            return Response({"error": message}, status=status_code)

# --- AY SONU TAHMİNİ ---

class ForecastView(APIView):
    """Month-end forecast for the dashboard (see finance/forecast.py)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Make sure today's due recurring items are recorded before forecasting
        bill_due_subscriptions(user=request.user)
        return Response(monthly_forecast(request.user))
