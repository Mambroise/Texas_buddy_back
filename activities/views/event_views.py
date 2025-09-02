# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/event_views.py
# Author : Morice
# ---------------------------------------------------------------------------

from rest_framework import generics, permissions
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.shortcuts import get_object_or_404

from ..models.event import Event
from ..serializers import EventDetailSerializer
from core.mixins import RetrieveLogMixin


# ─── Event by ID ─────────────────────────────────────────────────────────────
@method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True), name='dispatch')
class EventDetailAPIView(RetrieveLogMixin, generics.RetrieveAPIView):
    queryset = Event.objects.select_related('primary_category').prefetch_related('category', 'promotions')
    serializer_class = EventDetailSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

# ─── Event by place_id (optionnel) ───────────────────────────────────────────
@method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True), name='dispatch')
class EventDetailByPlaceIdAPIView(RetrieveLogMixin, generics.RetrieveAPIView):
    serializer_class = EventDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

    def get_object(self):
        place_id = self.kwargs["place_id"]
        qs = Event.objects.select_related('primary_category').prefetch_related('category', 'promotions')
        return get_object_or_404(qs, place_id=place_id)