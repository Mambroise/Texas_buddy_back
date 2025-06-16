# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/event_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from datetime import datetime
from django.utils import timezone
from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from ..models.event import Event
from ..serializers import EventSerializer
from ..filters import EventFilter


class EventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = EventFilter

    search_fields = ["title", "description", "location", "city"]
    ordering_fields = ["start_datetime", "price", "created_at"]
    ordering = ["start_datetime"]

    def get_queryset(self):
        queryset = Event.objects.filter(is_public=True).prefetch_related("category", "promotions")

        request = self.request
        date_str = request.query_params.get('date')
        try:
            reference_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()
        except ValueError:
            reference_date = timezone.now().date()

        # Ne renvoyer que les événements dont la date de référence est entre start et end
        return queryset.filter(
            start_datetime__date__lte=reference_date,
            end_datetime__date__gte=reference_date
        )


class EventDetailAPIView(generics.RetrieveAPIView):
    queryset = Event.objects.prefetch_related("category", "promotions")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

