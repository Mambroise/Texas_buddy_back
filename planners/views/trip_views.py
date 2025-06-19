# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/views/trip_views.py
# Author : Morice
# ---------------------------------------------------------------------------


import logging
from rest_framework import serializers
from rest_framework import status, permissions
from datetime import timedelta
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from ..models import Trip, TripDay
from ..serializers import TripSerializer, TripDaySerializer
from .base import RateLimitedAPIView

# ─── Logger Setup ──────────────────────────────────────────────────────────
logger = logging.getLogger('texasbuddy')

# ─── Trip Views ────────────────────────────────────────────────────────────

class TripListCreateView(RateLimitedAPIView, ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        logger.info("[TRIP_LIST] Trip list requested by user: %s", self.request.user.email)
        return Trip.objects.filter(user=self.request.user).prefetch_related(
        'days__steps'  
    )

    def perform_create(self, serializer):
        trip = serializer.save(user=self.request.user)
        logger.info("[TRIP_CREATE] New trip created by user %s: %s", self.request.user.email, trip)

        # Création automatique des TripDay
        current_date = trip.start_date
        while current_date <= trip.end_date:
            TripDay.objects.create(trip=trip, date=current_date)
            current_date += timedelta(days=1)
        logger.info("[TRIPDAY_AUTO_CREATE] %s days created for trip %s", (trip.end_date - trip.start_date).days + 1, trip.id)


@method_decorator(ratelimit(key='ip', rate='8/m', method='GET', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='8/m', method='PATCH', block=True), name='dispatch')
class TripDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        logger.info("[TRIP_DETAIL] Trip detail accessed by user: %s", self.request.user.email)
        return Trip.objects.filter(user=self.request.user).prefetch_related(
            'days__steps'   
        )

