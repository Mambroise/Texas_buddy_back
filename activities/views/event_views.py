# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/event_views.py
# Author : Morice
# ---------------------------------------------------------------------------

from rest_framework import generics, permissions
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from ..models.event import Event
from ..serializers import EventSerializer
from core.mixins import RetrieveLogMixin


# ─── View: EventDetailAPIView ──────────────────────────────────────────────
@method_decorator(ratelimit(key='ip', rate='8/m', method='GET', block=True), name='dispatch')
class EventDetailAPIView(RetrieveLogMixin,generics.RetrieveAPIView):
    queryset = Event.objects.prefetch_related("category", "promotions")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

