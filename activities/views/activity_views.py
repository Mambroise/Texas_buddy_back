# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/activity_views.py
# Author : Morice
# ---------------------------------------------------------------------------

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from core.mixins import RetrieveLogMixin
from ..models.activity import Activity
from ..serializers import ActivityDetailSerializer

# ─── View: ActivityDetailAPIView ────────────────────────────────────────────
@method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True), name='dispatch')
class ActivityDetailAPIView(RetrieveLogMixin, generics.RetrieveAPIView):
    queryset = Activity.objects.prefetch_related('category', 'promotions')
    serializer_class = ActivityDetailSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
    throttle_classes = [] # Disable throttling for this view, as it's already rate-limited by the base class
