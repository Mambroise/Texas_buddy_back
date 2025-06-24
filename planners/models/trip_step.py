# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/models/trip_step.py
# Author : Morice
# ---------------------------------------------------------------------------

from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .trip_day import TripDay

class TripStep(models.Model):
    TRANSPORT_MODES = [
        ('walking', 'Walking'),
        ('driving', 'Driving'),
        ('bicycling', 'Bicycling'),
        ('transit', 'Transit'),
    ]

    trip_day = models.ForeignKey(TripDay, on_delete=models.CASCADE, related_name="steps")
    activity = models.ForeignKey("activities.Activity", on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey("activities.Event", on_delete=models.SET_NULL, null=True, blank=True)

    start_time = models.TimeField()
    estimated_duration_minutes = models.PositiveIntegerField()
    
    # Transport details
    travel_mode = models.CharField(max_length=20, choices=TRANSPORT_MODES, default='walking')
    travel_duration_minutes = models.PositiveIntegerField(default=0)
    travel_distance_meters = models.PositiveIntegerField(default=0)

    end_time = models.TimeField(editable=False, null=True)  # Automatically calculated

    notes = models.TextField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["start_time"]

    def clean(self):
        if self.estimated_duration_minutes < 0:
            raise ValidationError(_("Estimated duration cannot be negative."))
        if self.travel_duration_minutes < 0:
            raise ValidationError(_("Travel duration cannot be negative."))
        if self.travel_distance_meters < 0:
            raise ValidationError(_("Travel distance cannot be negative."))

    def save(self, *args, **kwargs):
        self.full_clean()  # calling clean before saving

        # total_minutes = estimated + travel
        total_minutes = self.estimated_duration_minutes + self.travel_duration_minutes

        full_dt = datetime.combine(datetime.today(), self.start_time) + timedelta(minutes=total_minutes)
        self.end_time = full_dt.time()

        super().save(*args, **kwargs)
