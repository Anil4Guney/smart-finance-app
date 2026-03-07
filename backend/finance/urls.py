from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, SavingsGoalViewSet # SavingsGoalViewSet eklendi

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'savings-goals', SavingsGoalViewSet, basename='savings-goal') # Yeni köprümüz!

urlpatterns = [
    path('', include(router.urls)),
]