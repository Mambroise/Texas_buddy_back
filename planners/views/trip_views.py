# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/views/trip_views.py
# Author : Morice
# ---------------------------------------------------------------------------



from rest_framework import  permissions
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from ..models import Trip
from ..serializers import TripSerializer
from .base import RateLimitedAPIView
from core.mixins import ListLogMixin, CRUDLogMixin


# ─── Trip Views ────────────────────────────────────────────────────────────

class TripListCreateView(RateLimitedAPIView,ListLogMixin,CRUDLogMixin,ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user).prefetch_related(
        'days__steps'  
    )

    def perform_create(self, serializer):
        trip = serializer.save(user=self.request.user)

        # TripDay auto creation logic
        if trip.start_date and trip.end_date:
            trip.create_trip_days()

        # Optionnel mais propre : maj des dates (au cas où)
        trip.update_dates_from_days()



@method_decorator(ratelimit(key='ip', rate='8/m', method='GET', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='8/m', method='PATCH', block=True), name='dispatch')
class TripDetailView(RetrieveUpdateDestroyAPIView,ListLogMixin,CRUDLogMixin):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user).prefetch_related(
            'days__steps'   
        )

