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
from django.shortcuts import get_object_or_404

from core.mixins import RetrieveLogMixin
from ..models import Activity, Event
from ..serializers import (
    ActivityDetailSerializer
)

# ─── Activity by ID ──────────────────────────────────────────────────────────
@method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True), name='dispatch')
class ActivityDetailAPIView(RetrieveLogMixin, generics.RetrieveAPIView):
    queryset = Activity.objects.select_related('primary_category').prefetch_related('category', 'promotions')
    serializer_class = ActivityDetailSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
    throttle_classes = []  # Rate limit déjà appliqué

# ─── Activity by place_id (optionnel) ────────────────────────────────────────
@method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True), name='dispatch')
class ActivityDetailByPlaceIdAPIView(RetrieveLogMixin, generics.RetrieveAPIView):
    serializer_class = ActivityDetailSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = []

    def get_object(self):
        place_id = self.kwargs["place_id"]
        qs = Activity.objects.select_related('primary_category').prefetch_related('category', 'promotions')
        return get_object_or_404(qs, place_id=place_id)