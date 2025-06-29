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
    rate = '30/10m'
    method = 'GET'

    @classmethod
    def get_ratelimited_method(cls, func):
        return method_decorator(
            ratelimit(key='ip', rate=cls.rate, method=cls.method, block=True)
        )(func)

    def dispatch(self, request, *args, **kwargs):
        if request.method == self.method:
            self.dispatch = self.get_ratelimited_method(super().dispatch)
        return super().dispatch(request, *args, **kwargs)

class PostRateLimitedAPIView(APIView):
    rate = '30/10m'  # 30 requests per 10 minutes
    """Base APIView with rate limiting applied to POST requests."""
    method = 'POST'

    @classmethod
    def get_ratelimited_method(cls, func):
        return method_decorator(
            ratelimit(key='ip', rate=cls.rate, method=cls.method, block=True)
        )(func)

    def dispatch(self, request, *args, **kwargs):
        # Apply rate limiting only on POST requests
        if request.method == self.method:
            self.dispatch = self.get_ratelimited_method(super().dispatch)
        return super().dispatch(request, *args, **kwargs)
    

class PatchRateLimitedAPIView(APIView):
    """
    APIView avec rate limit sur PATCH.
    """
    rate = "10/10m"
    method = "PATCH"

    @classmethod
    def get_ratelimited_method(cls, func):
        return method_decorator(
            ratelimit(key="ip", rate=cls.rate, method=cls.method, block=True)
        )(func)

    def dispatch(self, request, *args, **kwargs):
        if request.method == self.method:
            self.dispatch = self.get_ratelimited_method(super().dispatch)
        return super().dispatch(request, *args, **kwargs)
    
class DeleteRateLimitedAPIView(APIView):
    rate = "7/10m"
    method = "DELETE"

    @classmethod
    def get_ratelimited_method(cls, func):
        return method_decorator(
            ratelimit(key="ip", rate=cls.rate, method=cls.method, block=True)
        )(func)

    def dispatch(self, request, *args, **kwargs):
        if request.method == self.method:
            self.dispatch = self.get_ratelimited_method(super().dispatch)
        return super().dispatch(request, *args, **kwargs)
