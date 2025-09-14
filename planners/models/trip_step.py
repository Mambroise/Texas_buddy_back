# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/models/trip_step.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta

class TripStep(models.Model):
    TRANSPORT_MODES = [
        ('walking', 'Walking'),
        ('driving', 'Driving'),
        ('bicycling', 'Bicycling'),
        ('transit', 'Transit'),
    ]

    trip_day = models.ForeignKey('TripDay', on_delete=models.CASCADE, related_name="steps")
    activity = models.ForeignKey("activities.Activity", on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey("activities.Event", on_delete=models.SET_NULL, null=True, blank=True)

    start_time = models.TimeField()
    estimated_duration_minutes = models.PositiveIntegerField()

    travel_mode = models.CharField(max_length=20, choices=TRANSPORT_MODES, default='driving')
    travel_duration_minutes = models.PositiveIntegerField(default=0)
    travel_distance_meters = models.PositiveIntegerField(default=0)

    end_time = models.TimeField(editable=False, null=True, blank=True)

    notes = models.TextField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["start_time"]

    def clean(self):
        errors = {}

        # Champs requis
        if self.start_time is None:
            errors['start_time'] = _("Start time is required.")
        if self.estimated_duration_minutes is None:
            errors['estimated_duration_minutes'] = _("Estimated duration is required.")
        else:
            if self.estimated_duration_minutes < 0:
                errors['estimated_duration_minutes'] = _("Estimated duration cannot be negative.")

        # Valeurs de transport : normaliser None -> 0 et vérifier
        if self.travel_duration_minutes is None:
            self.travel_duration_minutes = 0
        elif self.travel_duration_minutes < 0:
            errors['travel_duration_minutes'] = _("Travel duration cannot be negative.")

        if self.travel_distance_meters is None:
            self.travel_distance_meters = 0
        elif self.travel_distance_meters < 0:
            errors['travel_distance_meters'] = _("Travel distance cannot be negative.")

        if errors:
            # Lève des erreurs mappées aux champs dans l’admin
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Valider avant de calculer end_time
        self.full_clean()

        # Calcul d'end_time seulement si on a ce qu'il faut
        total_minutes = (self.estimated_duration_minutes or 0) + (self.travel_duration_minutes or 0)
        if self.start_time is not None:
            full_dt = datetime.combine(datetime.today(), self.start_time) + timedelta(minutes=total_minutes)
            self.end_time = full_dt.time()
        else:
            self.end_time = None

        super().save(*args, **kwargs)
