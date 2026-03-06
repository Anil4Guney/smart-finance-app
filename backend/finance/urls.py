from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'savings-goals', views.SavingsGoalViewSet, basename='savingsgoal')

urlpatterns = [
    path("", include(router.urls)),
    path("scan-receipt/", views.scan_receipt),
]
