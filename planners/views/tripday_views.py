# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/views/tripday_views.py
# Author : Morice
# ---------------------------------------------------------------------------


import logging
from datetime import timedelta
from rest_framework import serializers, status, permissions
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.response import Response
from rest_framework import status

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from core.mixins import ListLogMixin, RetrieveLogMixin
from ..models import TripDay
from ..serializers import TripDaySerializer
from core.throttles import  PostRateLimitedAPIView

# ─── Logger Setup ──────────────────────────────────────────────────────────
logger = logging.getLogger('texasbuddy')

# ─── TripDay Views ─────────────────────────────────────────────────────────

# --- LIST & CREATE : Log + RateLimit POST seulement ---
@method_decorator(ratelimit(key='ip', rate='30/10m', method='GET', block=True), name='dispatch')
class TripDayListCreateView(ListLogMixin, PostRateLimitedAPIView, ListCreateAPIView):
    serializer_class = TripDaySerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def get_queryset(self):
        return TripDay.objects.filter(trip__user=self.request.user)

    def perform_create(self, serializer):
        new_day = serializer.validated_data['date']
        trip = serializer.validated_data['trip']

        if trip.days.filter(date=new_day).exists():
            logger.warning("[TRIPDAY_DUPLICATE] Date %s already exists for trip %s", new_day, trip.id)
            raise serializers.ValidationError({"detail": _("This date already exists for the trip.")})

        # Recherche adresse à copier depuis jour avant ou après
        previous_day = trip.days.filter(date__lt=new_day).order_by('-date').first()
        next_day = trip.days.filter(date__gt=new_day).order_by('date').first()

        address_cache = None
        if previous_day and previous_day.address_cache:
            address_cache = previous_day.address_cache
        elif next_day and next_day.address_cache:
            address_cache = next_day.address_cache

        # Création TripDay avec adresse_cache copiée si trouvée
        day = serializer.save(address_cache=address_cache)

        # Mets à jour les bornes du trip en fonction des jours existants
        trip.update_dates_from_days()

        logger.info("[TRIPDAY_CREATE] New trip day %s created for trip %s with address cache %s", day.id, trip.id, address_cache.id if address_cache else "None")


# --- DETAIL / UPDATE / DELETE : Log + RateLimit GET & PATCH ---
@method_decorator(ratelimit(key='ip', rate='8/m', method='GET', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='8/m', method='PATCH', block=True), name='dispatch')
class TripDayDetailView(RetrieveLogMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = TripDaySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def get_queryset(self):
        logger.info("[TRIPDAY_DETAIL] Accessed by user: %s", self.request.user.email)
        return TripDay.objects.filter(trip__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        trip = instance.trip
        deleted_date = instance.date

        if trip.days.count() <= 1:
            logger.warning("[TRIPDAY_DELETE_BLOCKED] Attempt to delete last TripDay for trip %s by %s", trip.id, request.user.email)
            return Response(
                {"detail": _("Impossible to delete the last trip day.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)

        # Cascade: décaler les jours suivants (ceux avec une date > deleted_date)
        following_days = trip.days.filter(date__gt=deleted_date).order_by('date')
        for day in following_days:
            old_date = day.date
            day.date = old_date - timedelta(days=1)
            day.save(update_fields=['date'])
            logger.info("[TRIPDAY_SHIFT] TripDay %s moved from %s to %s", day.id, old_date, day.date)

        # Update trip dates
        trip.update_dates_from_days()

        logger.info("[TRIPDAY_DELETE] TripDay %s deleted by %s", instance.id, request.user.email)
        return Response(status=status.HTTP_204_NO_CONTENT)
