# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/event_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from ..models.event import Event
from ..serializers import EventSerializer

class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.filter(is_public=True).select_related().prefetch_related("category", "promotions")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["city", "state", "category__name"]
    ordering_fields = ["start_datetime", "price", "created_at"]
    
    search_fields = ["title", "description", "location", "city"]

class EventDetailAPIView(generics.RetrieveAPIView):
    queryset = Event.objects.prefetch_related("category", "promotions")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
