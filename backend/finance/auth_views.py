"""Login and logout endpoints (JWT)."""
from rest_framework.throttling import SimpleRateThrottle
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView


class LoginRateThrottle(SimpleRateThrottle):
    """
    Limits login attempts per username (not per IP: behind a proxy every visitor can look
    like the same address, and the header can be forged). Slows down password guessing.
    """
    scope = 'login'

    def get_cache_key(self, request, view):
        username = str(request.data.get('username', '')).strip().lower()[:150]
        if not username:
            return None  # nothing to guess for; the serializer rejects the request anyway
        return self.cache_format % {'scope': self.scope, 'ident': username}


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]


class LogoutView(TokenBlacklistView):
    """POST {"refresh": "..."}: the refresh token can no longer be used."""
