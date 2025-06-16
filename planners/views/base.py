# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/views/base.py
# Author : Morice
# ---------------------------------------------------------------------------

from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

class RateLimitedAPIView(APIView):
    rate = '8/m'
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
