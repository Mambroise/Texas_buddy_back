# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/views/tripstep_views.py
# Author : Morice
# ---------------------------------------------------------------------------

import logging
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from core.mixins import ListLogMixin, CRUDLogMixin
from drf_spectacular.utils import extend_schema, OpenApiExample
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _

from ..models import TripStep, TripDay
from ..serializers import TripStepSerializer, TripStepMoveSerializer
from .base import RateLimitedAPIView

# ─── Logger Setup ──────────────────────────────────────────────────────────
logger = logging.getLogger('texasbuddy')


# ─── TripStep List & Create View ────────────────────────────────────────────
class TripStepListCreateView(ListLogMixin, RateLimitedAPIView, ListCreateAPIView):
    serializer_class = TripStepSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TripStep.objects.filter(trip_day__trip__user=self.request.user)



# ─── TripStep Move View ─────────────────────────────────────────────────────
@method_decorator(ratelimit(key='ip', rate='8/m', method='PATCH', block=True), name='dispatch')
class TripStepMoveView(RateLimitedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            step = TripStep.objects.get(pk=pk, trip_day__trip__user=request.user)
        except TripStep.DoesNotExist:
            logger.warning("[TRIPSTEP_MOVE] Attempted to move non-existent TripStep (id=%s) by %s", pk, request.user.email)
            return Response({"detail": _("TripStep not found.")}, status=status.HTTP_404_NOT_FOUND)

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

        return Response({"message": _("TripStep moved and adjusted successfully.")}, status=status.HTTP_200_OK)


# ─── TripDay Sync View ──────────────────────────────────────────────────────

@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "nullable": True},
                            "start_time": {"type": "string", "format": "time"},
                            "estimated_duration_minutes": {"type": "integer"},
                            "activity_id": {"type": "integer", "nullable": True},
                            "event_id": {"type": "integer", "nullable": True},
                            "travel_mode": {"type": "string", "nullable": True},
                            "travel_duration_minutes": {"type": "integer", "nullable": True},
                            "travel_distance_meters": {"type": "integer", "nullable": True},
                            "notes": {"type": "string", "nullable": True},
                        },
                        "required": ["start_time", "estimated_duration_minutes"]
                    }
                }
            }
        }
    },
    responses={
        200: OpenApiExample(
            'Success',
            value={
                "message": "TripSteps updated and rearranged.",
                "updated": 3,
                "created": 1
            },
            response_only=True
        )
    },
    description="Synchronize the list of TripSteps for the given TripDay. Allows creation and update of TripSteps, and automatically adjusts overlapping start times."
)
@method_decorator(ratelimit(key='ip', rate='30/10m', method='POST', block=True), name='dispatch')
class TripDaySyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        trip_day = get_object_or_404(TripDay, pk=pk, trip__user=request.user)
        steps_data = request.data.get("steps", [])

        if not isinstance(steps_data, list):
            logger.warning("[TRIPDAY_SYNC] Invalid 'steps' payload from %s for TripDay %s", request.user.email, pk)
            return Response({"detail": _("Trip steps should be a list.")}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("[TRIPDAY_SYNC] Sync request received by %s for TripDay %s (%d steps)", request.user.email, pk, len(steps_data))

        id_to_step = {step.id: step for step in trip_day.steps.all()}
        updated_steps = []
        created_steps = []

        for step_data in steps_data:
            step_id = step_data.get("id")
            step_data["trip_day"] = trip_day.id  # for creation

            if step_id and step_id in id_to_step:
                # Update existing
                step = id_to_step[step_id]
                serializer = TripStepSerializer(step, data=step_data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                updated_steps.append(step)
                logger.info("[TRIPDAY_SYNC] Updated TripStep id=%s", step.id)

            else:
                # Create new TripStep
                serializer = TripStepSerializer(data=step_data)
                serializer.is_valid(raise_exception=True)
                step = serializer.save()
                created_steps.append(step)
                logger.info("[TRIPDAY_SYNC] Created new TripStep id=%s", step.id)

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
            "[TRIPDAY_SYNC_DONE] TripDay %s synchronized by %s - %d updated, %d created",
            pk, request.user.email, len(updated_steps), len(created_steps)
        )

        return Response({
            "message": "TripSteps updated and rearranged.",
            "updated": len(updated_steps),
            "created": len(created_steps),
        }, status=status.HTTP_200_OK)


# ─── TripStep Delete View ───────────────────────────────────────────────────
class TripStepDeleteView(CRUDLogMixin, RateLimitedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            step = TripStep.objects.get(pk=pk, trip_day__trip__user=request.user)
        except TripStep.DoesNotExist:
            return Response({"detail": _("Trip step not found.")}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(step)
        return Response({"message": _("Trip step deleted.")}, status=status.HTTP_204_NO_CONTENT)
