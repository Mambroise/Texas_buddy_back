# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/views/tripstep_views.py
# Author : Morice
# ---------------------------------------------------------------------------

import logging
from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView

from ..models import TripStep, TripDay
from ..serializers import TripStepSerializer, TripStepMoveSerializer
from .base import RateLimitedAPIView

# ─── Logger Setup ──────────────────────────────────────────────────────────
logger = logging.getLogger('texasbuddy')


# ─── TripStep List & Create View ────────────────────────────────────────────
class TripStepListCreateView(RateLimitedAPIView, ListCreateAPIView):
    serializer_class = TripStepSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        logger.info("[TRIPSTEP_LIST] TripSteps requested by user: %s", self.request.user.email)
        return TripStep.objects.filter(day__trip__user=self.request.user)

    def perform_create(self, serializer):
        step = serializer.save()
        logger.info("[TRIPSTEP_CREATE] New TripStep created (id=%s) by %s", step.id, self.request.user.email)


# ─── TripStep Move View ─────────────────────────────────────────────────────
class TripStepMoveView(RateLimitedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            step = TripStep.objects.get(pk=pk, trip_day__trip__user=request.user)
        except TripStep.DoesNotExist:
            logger.warning("[TRIPSTEP_MOVE] Attempted to move non-existent TripStep (id=%s) by %s", pk, request.user.email)
            return Response({"detail": "TripStep not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TripStepMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_start = serializer.validated_data["start_time"]

        # Update the moved step
        old_start = step.start_time
        step.start_time = new_start
        step.save()  # triggers automatic recalculation of end_time

        logger.info(
            "[TRIPSTEP_MOVE] TripStep %s moved from %s to %s by %s",
            step.id, old_start, new_start, request.user.email
        )

        # Cascade update of following steps in the same TripDay
        other_steps = TripStep.objects.filter(
            trip_day=step.trip_day
        ).exclude(id=step.id).order_by('start_time')

        current_end = step.end_time
        domino_count = 0

        for other in other_steps:
            if other.start_time < current_end:
                logger.debug(
                    "[TRIPSTEP_MOVE_DOMINO] Adjusting TripStep %s from %s to %s",
                    other.id, other.start_time, current_end
                )
                other.start_time = current_end
                other.save()  # triggers recalculation of end_time
                current_end = other.end_time
                domino_count += 1

        logger.info(
            "[TRIPSTEP_MOVE_DONE] TripStep %s moved with domino effect on %d steps.",
            step.id, domino_count
        )

        return Response({"message": "TripStep moved and adjusted successfully."}, status=status.HTTP_200_OK)


# ─── TripDay Sync View ──────────────────────────────────────────────────────
class TripDaySyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        trip_day = get_object_or_404(TripDay, pk=pk, trip__user=request.user)
        steps_data = request.data.get("steps", [])

        if not isinstance(steps_data, list):
            logger.warning("[TRIPDAY_SYNC] Invalid 'steps' payload from %s for TripDay %s", request.user.email, pk)
            return Response({"detail": "Steps should be a list."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("[TRIPDAY_SYNC] Sync request received by %s for TripDay %s (%d steps)", request.user.email, pk, len(steps_data))

        id_to_step = {step.id: step for step in trip_day.steps.all()}
        updated_steps = []

        for step_data in steps_data:
            step_id = step_data.get("id")
            if not step_id or step_id not in id_to_step:
                logger.debug("[TRIPDAY_SYNC] Ignored unknown TripStep id=%s", step_id)
                continue

            step = id_to_step[step_id]
            serializer = TripStepSerializer(step, data=step_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            updated_steps.append(step)

            logger.info("[TRIPDAY_SYNC] Updated TripStep id=%s", step.id)

        # Reorder steps with cascading adjustments
        trip_steps = trip_day.steps.order_by("start_time").all()
        timeline = []

        for step in trip_steps:
            if not timeline:
                timeline.append(step)
                continue

            previous = timeline[-1]
            expected_start = previous.end_time
            if step.start_time < expected_start:
                logger.debug(
                    "[TRIPDAY_SYNC_ADJUST] TripStep %s moved from %s to %s",
                    step.id, step.start_time, expected_start
                )
                step.start_time = expected_start
                step.save()

            timeline.append(step)

        logger.info(
            "[TRIPDAY_SYNC_DONE] TripDay %s synchronized by %s - %d steps updated",
            pk, request.user.email, len(updated_steps)
        )

        return Response({"message": "TripSteps updated and rearranged."}, status=status.HTTP_200_OK)


# ─── TripStep Delete View ───────────────────────────────────────────────────
class TripStepDeleteView(RateLimitedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            step = TripStep.objects.get(pk=pk, trip_day__trip__user=request.user)
        except TripStep.DoesNotExist:
            logger.warning("[TRIPSTEP_DELETE] Attempted to delete non-existent TripStep (id=%s) by %s", pk, request.user.email)
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        logger.info("[TRIPSTEP_DELETE] TripStep %s deleted by %s", step.id, request.user.email)
        step.delete()

        return Response({"message": "TripStep deleted."}, status=status.HTTP_204_NO_CONTENT)
