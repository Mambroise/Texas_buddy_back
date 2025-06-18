# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/views/tripday_views.py
# Author : Morice
# ---------------------------------------------------------------------------


import logging
from rest_framework import serializers
from rest_framework import status, permissions
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from ..models import  TripDay
from ..serializers import  TripDaySerializer
from .base import RateLimitedAPIView

# ─── Logger Setup ──────────────────────────────────────────────────────────
logger = logging.getLogger('texasbuddy')

# ─── TripDay Views ─────────────────────────────────────────────────────────

class TripDayListCreateView(RateLimitedAPIView, ListCreateAPIView):
    serializer_class = TripDaySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        logger.info("[TRIPDAY_LIST] Trip days requested by user: %s", self.request.user.email)
        return TripDay.objects.filter(trip__user=self.request.user)

def perform_create(self, serializer):
    new_day = serializer.validated_data['date']
    trip = serializer.validated_data['trip']

    if trip.days.filter(date=new_day).exists():
        logger.warning("[TRIPDAY_DUPLICATE] Date %s already exists for trip %s", new_day, trip.id)
        raise serializers.ValidationError({"detail": "Cette date est déjà planifiée dans le voyage."})

    day = serializer.save()

    # Mets à jour les bornes du trip en fonction des jours existants
    trip.update_dates_from_days()

    logger.info("[TRIPDAY_CREATE] New trip day %s created for trip %s", day.id, trip.id)

@method_decorator(ratelimit(key='ip', rate='8/m', method='GET', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='8/m', method='PATCH', block=True), name='dispatch')
class TripDayDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TripDaySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        logger.info("[TRIPDAY_DETAIL] Accessed by user: %s", self.request.user.email)
        return TripDay.objects.filter(trip__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        trip = instance.trip

        if trip.days.count() <= 1:
            logger.warning("[TRIPDAY_DELETE_BLOCKED] Attempt to delete last TripDay for trip %s by %s", trip.id, request.user.email)
            return Response(
                {"detail": "Impossible de supprimer le dernier jour du voyage."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)

        # Update trip dates after deleting
        trip.update_dates_from_days()

        logger.info("[TRIPDAY_DELETE] TripDay %s deleted by %s", instance.id, request.user.email)
        return Response(status=status.HTTP_204_NO_CONTENT)
