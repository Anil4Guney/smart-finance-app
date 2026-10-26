"""
URL configuration for SmartFinance config project.
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include

from finance.auth_views import LogoutView, ThrottledTokenObtainPairView

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('api/', include('finance.urls')),
    # Our own login (rate limited per username) and logout (invalidates the refresh token)
    path('auth/jwt/create/', ThrottledTokenObtainPairView.as_view(), name='jwt-create'),
    path('auth/jwt/logout/', LogoutView.as_view(), name='jwt-logout'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
