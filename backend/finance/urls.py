from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Tüm View ve ViewSet'lerimizi içeri aktarıyoruz
from .views import (
    TransactionViewSet, 
    SavingsGoalViewSet, 
    CategoryBudgetViewSet, 
    SubscriptionViewSet,
    AIChatView,
    scan_receipt
)

# Router, otomatik olarak GET, POST, PUT, DELETE yollarını (endpoint) oluşturur
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'savings-goals', SavingsGoalViewSet, basename='savings-goal')
router.register(r'budgets', CategoryBudgetViewSet, basename='budget') # Bütçeler eklendi
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription') # Abonelikler eklendi

urlpatterns = [
    # Router'ın oluşturduğu tüm otomatik yolları ana URL'e dahil et
    path('', include(router.urls)),
    
    # Özel yollar (View ve API_View'ler)
    path('chat/', AIChatView.as_view(), name='ai-chat'), # Yeni Chatbot linkimiz! (Frontend'deki /chat/ isteğini karşılar)
    path('scan-receipt/', scan_receipt, name='scan-receipt'), # Fiş tarama AI linki
]