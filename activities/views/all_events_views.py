# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/all_events_views.py
# Author : Morice
# ---------------------------------------------------------------------------

from datetime import datetime
from django.utils import timezone
from rest_framework import generics
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.http import Http404

from ..models import Event
from ..serializers import EventListSerializer
from core.mixins import ListLogMixin


# ─── View: CurrentYearEventsList ───────────────────────────────────────────
# Return all public events overlapping current year
@method_decorator(ratelimit(key='ip', rate='12/m', method='GET', block=True), name='dispatch')
class CurrentYearEventsList(ListLogMixin, generics.ListAPIView):
    serializer_class = EventListSerializer
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def get_queryset(self):
        now = timezone.now()
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        year_end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)

        queryset = Event.objects.filter(
            start_datetime__lte=year_end,
            end_datetime__gte=year_start,
            is_public=True  # Only public events
        ).select_related("primary_category").prefetch_related("category", "promotions").order_by("start_datetime")

        return queryset


# ─── View: EventsInBoundsList ─────────────────────────────────────────────
# Return public events overlapping the requested year AND within map bounds
# GET /api/events/in-bounds/?north=..&south=..&east=..&west=..&zoom=..&year=2025
class EventsInBoundsList(ListLogMixin, generics.ListAPIView):
    serializer_class = EventListSerializer
    throttle_classes = []

    def _parse_bounds(self, request):
        try:
            north = float(request.query_params.get("north"))
            south = float(request.query_params.get("south"))
            east  = float(request.query_params.get("east"))
            west  = float(request.query_params.get("west"))
        except (TypeError, ValueError):
            raise Http404("Invalid or missing bounds (north/south/east/west)")
        return north, south, east, west

    def _year_range(self, year: int):
        # utilise le tz courant pour rester "aware"
        now = timezone.now()
        y_start = now.replace(year=year, month=1,  day=1,  hour=0,  minute=0,  second=0,  microsecond=0)
        y_end   = now.replace(year=year, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        return y_start, y_end

    def get_queryset(self):
        north, south, east, west = self._parse_bounds(self.request)

        # year param optionnel (défaut: année courante)
        year_param = self.request.query_params.get("year")
        try:
            year = int(year_param) if year_param else timezone.now().year
        except ValueError:
            year = timezone.now().year

        zoom_param = self.request.query_params.get("zoom")
        try:
            zoom = int(zoom_param) if zoom_param is not None else 10
        except ValueError:
            zoom = 10

        year_start, year_end = self._year_range(year)

        qs = (
            Event.objects.filter(
                start_datetime__lte=year_end,
                end_datetime__gte=year_start,
                is_public=True,
                latitude__isnull=False, longitude__isnull=False,
                latitude__gte=south, latitude__lte=north,
                longitude__gte=west,  longitude__lte=east,
            )
            .select_related("primary_category")
            .prefetch_related("category", "promotions")
            .order_by("start_datetime")
        )

        # Sécurité en très faible zoom (monde/état) : on borne le volume
        if zoom < 8:
            qs = qs[:1000]

        return qs
