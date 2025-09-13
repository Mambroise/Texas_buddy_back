# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : planners/views/trip_views.py
# Author : Morice
# ---------------------------------------------------------------------------

from rest_framework import permissions, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from ..models import Trip
from ..serializers import TripSerializer
from core.mixins import ListLogMixin, CRUDLogMixin
from core.throttles import PostRateLimitedAPIView

# ─── Trip Views ────────────────────────────────────────────────────────────

class TripListCreateView(PostRateLimitedAPIView, ListLogMixin, CRUDLogMixin, ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []  # Déjà limité par la classe de base

    def get_queryset(self):
        # Préfetch utile pour liste + détail (days/steps)
        return (
            Trip.objects.filter(user=self.request.user)
            .prefetch_related('days__steps')
        )

    def perform_create(self, serializer):
        trip = serializer.save(user=self.request.user)

        # Création auto des TripDay si dates présentes
        if trip.start_date and trip.end_date:
            # Suppose que ton modèle expose ces helpers:
            # - create_trip_days()
            # - update_dates_from_days()
            trip.create_trip_days()

        # Harmonisation (au cas où)
        trip.update_dates_from_days()


@method_decorator(ratelimit(key='ip', rate='12/m', method='GET', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='12/m', method='PATCH', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='12/m', method='DELETE', block=True), name='dispatch')
class TripView(RetrieveUpdateDestroyAPIView, ListLogMixin, CRUDLogMixin):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []
    lookup_field = 'id'

    def get_queryset(self):
        return (
            Trip.objects.filter(user=self.request.user)
            .prefetch_related('days__steps')
        )

    def perform_update(self, serializer):
        # Si tu veux réagir à un changement de plage de dates:
        instance: Trip = self.get_object()
        old_start, old_end = instance.start_date, instance.end_date

        trip: Trip = serializer.save()

        # Si la plage change, on peut resynchroniser les days:
        if (old_start != trip.start_date) or (old_end != trip.end_date):
            # Si tu as une méthode dédiée, appelle-la ici (sinon, laisse comme ci-dessous).
            # trip.rebuild_trip_days()  # <— optionnel si tu l'as
            pass

        trip.update_dates_from_days()

    def destroy(self, request, *args, **kwargs):
        # Response explicite 204 + logs via CRUDLogMixin
        instance: Trip = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance: Trip):
        # Si CASCADE est en place sur TripDay/Step, ceci suffit.
        # Sinon, gère les suppressions enfants ici avant de delete le trip.
        instance.delete()
