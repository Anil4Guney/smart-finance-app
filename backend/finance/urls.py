from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, SavingsGoalViewSet, AIAdvisorView # AIAdvisorView eklendi

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'savings-goals', SavingsGoalViewSet, basename='savings-goal')

urlpatterns = [
    path('', include(router.urls)),
    path('advisor/', AIAdvisorView.as_view(), name='ai-advisor'), # Yapay Zeka linkimiz!
]