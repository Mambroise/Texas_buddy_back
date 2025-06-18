# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/event_views.py
# Author : Morice
# ---------------------------------------------------------------------------

from rest_framework import generics, permissions

from ..models.event import Event
from ..serializers import EventSerializer
from core.mixins import RetrieveLogMixin


# ─── View: EventDetailAPIView ──────────────────────────────────────────────
class EventDetailAPIView(RetrieveLogMixin,generics.RetrieveAPIView):
    queryset = Event.objects.prefetch_related("category", "promotions")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

