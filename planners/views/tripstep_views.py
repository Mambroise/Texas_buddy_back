# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/views/tripstepr_views.py
# Author : Morice
# ---------------------------------------------------------------------------



import logging
from django.shortcuts import get_object_or_404
from datetime import timedelta
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
)

from ..models import TripStep,TripDay
from ..serializers import TripStepSerializer, TripStepMoveSerializer
from .base import RateLimitedAPIView

# ─── Logger Setup ──────────────────────────────────────────────────────────
logger = logging.getLogger('texasbuddy')


class TripStepListCreateView(RateLimitedAPIView, ListCreateAPIView):
    serializer_class = TripStepSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        logger.info("[TRIPSTEP_LIST] Trip steps requested by user: %s", self.request.user.email)
        return TripStep.objects.filter(day__trip__user=self.request.user)

    def perform_create(self, serializer):
        step = serializer.save()
        logger.info("[TRIPSTEP_CREATE] New trip step created: %s by %s", step, self.request.user.email)


class TripStepMoveView(RateLimitedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            step = TripStep.objects.get(pk=pk, trip_day__trip__user=request.user)
        except TripStep.DoesNotExist:
            return Response({"detail": "TripStep not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TripStepMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_start = serializer.validated_data["start_time"]

        # Mise à jour du step déplacé
        step.start_time = new_start
        step.save()  # → recalcul automatique de end_time via .save()

        # Décalage automatique : on récupère les autres steps du même TripDay
        other_steps = TripStep.objects.filter(
            trip_day=step.trip_day
        ).exclude(id=step.id).order_by('start_time')

        # Effet domino : on décale tout ce qui chevauche
        current_end = step.end_time
        for other in other_steps:
            if other.start_time < current_end:
                other.start_time = current_end
                other.save()  # → recalcul automatique de end_time
                current_end = other.end_time

        logger.info(
            f"[TRIPSTEP_MOVE] TripStep {step.id} déplacée à {new_start} par {request.user.email} "
            f"avec effet domino sur {other_steps.count()} steps."
        )

        return Response({"message": "TripStep moved and adjusted successfully."}, status=status.HTTP_200_OK)


class TripDaySyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        trip_day = get_object_or_404(TripDay, pk=pk, trip__user=request.user)
        steps_data = request.data.get("steps", [])

        if not isinstance(steps_data, list):
            return Response({"detail": "Steps should be a list."}, status=status.HTTP_400_BAD_REQUEST)

        id_to_step = {step.id: step for step in trip_day.steps.all()}
        updated_steps = []

        for step_data in steps_data:
            step_id = step_data.get("id")
            if not step_id or step_id not in id_to_step:
                continue  # ignore invalid IDs

            step = id_to_step[step_id]

            serializer = TripStepSerializer(step, data=step_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            updated_steps.append(step)

        # ⚙️ Réorganiser les TripSteps en cascade, effet domino
        trip_steps = trip_day.steps.order_by("start_time").all()
        timeline = []

        for step in trip_steps:
            if not timeline:
                timeline.append(step)
                continue

            previous = timeline[-1]
            expected_start = previous.end_time  # ⚠️ On s’appuie désormais sur end_time
            if step.start_time < expected_start:
                logger.debug(f"Adjusting {step.id} from {step.start_time} to {expected_start}")
                step.start_time = expected_start
                step.save()  # → recalcul automatique de end_time

            timeline.append(step)

        return Response({"message": "TripSteps updated and rearranged."}, status=status.HTTP_200_OK)


class TripStepDeleteView(RateLimitedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            step = TripStep.objects.get(pk=pk, trip_day__trip__user=request.user)
        except TripStep.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        logger.info(f"Suppression de TripStep {step.id} par {request.user.email}")
        step.delete()
        return Response({"message": "TripStep supprimée."}, status=status.HTTP_204_NO_CONTENT)

