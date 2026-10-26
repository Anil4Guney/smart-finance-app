"""Small request/response safety nets that apply to every endpoint."""
from django.conf import settings
from django.http import JsonResponse


class RequestSizeLimitMiddleware:
    """
    Refuse oversized requests before Django reads (or writes to disk) any of the body.

    Without this a multipart upload is streamed to a temporary file before the view can
    check its size, so one huge upload could fill the disk.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            length = int(request.META.get('CONTENT_LENGTH') or 0)
        except ValueError:
            length = 0
        if length > settings.MAX_REQUEST_BYTES:
            return JsonResponse({'detail': 'İstek çok büyük.'}, status=413)
        return self.get_response(request)


class NoStoreMiddleware:
    """API and login responses hold personal data: browsers and proxies must not keep a copy."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(('/api/', '/auth/')):
            response['Cache-Control'] = 'no-store'
        return response
