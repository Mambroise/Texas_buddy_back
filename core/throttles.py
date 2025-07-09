# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :core/throttles.py
# Author : Morice
# ---------------------------------------------------------------------------

from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit


class GetRateLimitedAPIView(APIView):
    """APIView avec rate limit appliqué uniquement aux requêtes GET."""
    rate = '3/1m'
    method = 'GET'

    @method_decorator(ratelimit(key='ip', rate=rate, method=method, block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class PostRateLimitedAPIView(APIView):
    """APIView avec rate limit appliqué uniquement aux requêtes POST."""
    rate = '3/1m'
    method = 'POST'

    @method_decorator(ratelimit(key='ip', rate=rate, method=method, block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class PatchRateLimitedAPIView(APIView):
    """APIView avec rate limit appliqué uniquement aux requêtes PATCH."""
    rate = '10/10m'
    method = 'PATCH'

    @method_decorator(ratelimit(key='ip', rate=rate, method=method, block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class DeleteRateLimitedAPIView(APIView):
    """APIView avec rate limit appliqué uniquement aux requêtes DELETE."""
    rate = '7/10m'
    method = 'DELETE'

    @method_decorator(ratelimit(key='ip', rate=rate, method=method, block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
