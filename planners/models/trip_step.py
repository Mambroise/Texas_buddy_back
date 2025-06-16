# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/models/trip_step.py
# Author : Morice
# ---------------------------------------------------------------------------


from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from .trip_day import TripDay


class TripStep(models.Model):
    trip_day = models.ForeignKey(TripDay, on_delete=models.CASCADE, related_name="steps")
    activity = models.ForeignKey("activities.Activity", on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey("activities.Event", on_delete=models.SET_NULL, null=True, blank=True)

    start_time = models.TimeField()
    estimated_duration_minutes = models.PositiveIntegerField()
    travel_time_minutes = models.PositiveIntegerField(default=0)

    end_time = models.TimeField(editable=False, null=True)  # ← Ajouté

    notes = models.TextField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["start_time"]

    def clean(self):
        if self.estimated_duration_minutes < 0:
            raise ValidationError("Estimated duration cannot be negative.")
        if self.travel_time_minutes < 0:
            raise ValidationError("Travel time cannot be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()  # calling clean before saving

        total_minutes = self.estimated_duration_minutes + self.travel_time_minutes
        full_dt = datetime.combine(datetime.today(), self.start_time) + timedelta(minutes=total_minutes)
        self.end_time = full_dt.time()

        super().save(*args, **kwargs)