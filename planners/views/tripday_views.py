# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/views/tripday_views.py
# Author : Morice
# ---------------------------------------------------------------------------


import logging
from rest_framework import serializers
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.response import Response
from planners.services.address_service import get_or_create_address_cache_from_place_id

from ..models import  TripDay
from ..serializers import  TripDaySerializer,TripDayAddressUpdateSerializer
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


class TripDayAddressUpdateView(APIView):
#     {
#   "trip_day_id": 42,
#   "address": "xxx",
#   "place_id": "yyy"
# }
    def post(self, request, *args, **kwargs):
        serializer = TripDayAddressUpdateSerializer(data=request.data)
        if serializer.is_valid():
            trip_day_id = serializer.validated_data['trip_day_id']
            address = serializer.validated_data['address']
            place_id = serializer.validated_data['place_id']

            try:
                trip_day = TripDay.objects.get(id=trip_day_id)
            except TripDay.DoesNotExist:
                return Response({"error": "TripDay not found"}, status=status.HTTP_404_NOT_FOUND)

            # Lookup lat/lng
            cache = get_or_create_address_cache_from_place_id(address, place_id)

            # Update current TripDay
            trip_day.address_cache = cache
            trip_day.save()

            # Propagation
            TripDay.objects.filter(
                trip=trip_day.trip,
                date__gt=trip_day.date
            ).update(
                address_cache=cache
            )

            return Response({
                "updated_trip_day_id": trip_day_id,
                "new_address": cache.address,
                "latitude": cache.latitude,
                "longitude": cache.longitude,
                "propagation_count": TripDay.objects.filter(trip=trip_day.trip, date__gt=trip_day.date).count(),
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
