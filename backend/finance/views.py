import os
import google.generativeai as genai
from django.conf import settings

from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction, SavingsGoal
from .serializers import TransactionSerializer, SavingsGoalSerializer
from .services import analyze_receipt

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
        # Sadece giriş yapan kullanıcının hedeflerini getirir
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Yeni hedef eklendiğinde, o anki kullanıcıya bağlar
        serializer.save(user=self.request.user)


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


class AIAdvisorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)
        goals = SavingsGoal.objects.filter(user=request.user)

        # views.py içinde AIAdvisorView altındaki hesaplamayı şöyle güncelle:
        total_income = sum(float(t.amount) for t in transactions if t.transaction_type == 'INCOME')
        total_expense = sum(float(t.amount) for t in transactions if t.transaction_type == 'EXPENSE')

        # Yapay zekaya göndermek için verileri kısa metinlere çeviriyoruz
        tx_details = ", ".join([f"{t.title} (${t.amount})" for t in transactions[:10]])
        goal_details = ", ".join([f"{g.title} (${g.current_amount}/${g.target_amount})" for g in goals])

        prompt = f"""
        Sen uzman, samimi ve modern bir finansal danışmansın. 
        Kullanıcının toplam geliri: ${total_income}, toplam gideri: ${total_expense}.
        Son işlemleri: {tx_details}
        Birikim hedefleri: {goal_details}

        Lütfen bu verilere dayanarak kullanıcıya tam olarak 3 adet, aksiyon odaklı, kısa ve öz finansal tavsiye ver.
        Harcamalarını nasıl optimize edebileceğini ve hedeflerine nasıl daha hızlı ulaşabileceğini söyle.
        
        **ÖNEMLİ:** Çıktıyı tam olarak aşağıdaki JSON formatında, hiçbir Markdown etiketi (örneğin ```json) kullanmadan döndür:
        [
          {{
            "id": 1,
            "title": "Tavsiye Başlığı (Maks 5 kelime)",
            "content": "Tavsiye içeriği (Maks 2 cümle)"
          }},
          ...
        ]
        
        Sadece İngilizce dilinde tavsiye ver. Gereksiz emoji kullanma, sadece önemli yerler için 1-2 emoji kullanabilirsin.
        """

        try:
            # Şifreyi doğrudan settings üzerinden çekiyoruz (O da .env'den alıyor)
            api_key = settings.GEMINI_API_KEY
            
            if not api_key:
                return Response({"error": "API Key .env dosyasından okunamadı!"}, status=400)

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            return Response({"advice": response.text})
        except Exception as e:
            return Response({"error": str(e)}, status=500)