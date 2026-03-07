from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Transaction, SavingsGoal
from .serializers import TransactionSerializer, SavingsGoalSerializer
from .services import analyze_receipt
from rest_framework import permissions
from rest_framework import viewsets, permissions


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class SavingsGoalViewSet(viewsets.ModelViewSet):
    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)


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


class SavingsGoalViewSet(viewsets.ModelViewSet):
    serializer_class = SavingsGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Sadece giriş yapan kullanıcının hedeflerini getirir
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Yeni hedef eklendiğinde, o anki kullanıcıya bağlar
        serializer.save(user=self.request.user)