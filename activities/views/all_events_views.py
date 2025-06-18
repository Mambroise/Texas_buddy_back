# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/all_events_views.py
# Author : Morice
# ---------------------------------------------------------------------------

from django.utils import timezone
from rest_framework import generics
from ..models import Event
from ..serializers import EventSerializer
from core.mixins import ListLogMixin


# ─── View: CurrentYearEventsList ───────────────────────────────────────────
# Return all public events overlapping current year
class CurrentYearEventsList(ListLogMixin,generics.ListAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        now = timezone.now()
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        year_end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)

        queryset = Event.objects.filter(
            start_datetime__lte=year_end,
            end_datetime__gte=year_start,
            is_public=True  # Only public events
        )

        return queryset
