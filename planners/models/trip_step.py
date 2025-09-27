# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : planners/models/trip_step.py
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

    # ---------- Helpers temps ----------
    def _blocked_window(self):
        """
        Renvoie (dt_start_blocked, dt_end_blocked) sur la date du TripDay.
        Fenêtre = [start_time - travel_duration, start_time + estimated_duration]
        travel_duration_minutes: None -> 0
        """
        day_date = getattr(self.trip_day, "date", None)
        if day_date is None:
            # fallback : aujourd’hui (tjs même journée pour comparer des times)
            day_date = datetime.today().date()

        travel = (self.travel_duration_minutes or 0)
        activity = (self.estimated_duration_minutes or 0)

        start_dt = datetime.combine(day_date, self.start_time) - timedelta(minutes=travel)
        end_dt   = datetime.combine(day_date, self.start_time) + timedelta(minutes=activity)
        return start_dt, end_dt

    @staticmethod
    def _overlap(a_start, a_end, b_start, b_end) -> bool:
        # Chevauchement si les intervalles se coupent (bords inclus)
        return not (a_end <= b_start or b_end <= a_start)

    # ---------- Validation ----------
    def clean(self):
        errors = {}

        # Champs requis + bornes
        if self.start_time is None:
            errors['start_time'] = _("Start time is required.")
        if self.estimated_duration_minutes is None:
            errors['estimated_duration_minutes'] = _("Estimated duration is required.")
        elif self.estimated_duration_minutes < 0:
            errors['estimated_duration_minutes'] = _("Estimated duration cannot be negative.")

        # Normaliser None -> 0
        if self.travel_duration_minutes is None:
            self.travel_duration_minutes = 0
        elif self.travel_duration_minutes < 0:
            errors['travel_duration_minutes'] = _("Travel duration cannot be negative.")

        if self.travel_distance_meters is None:
            self.travel_distance_meters = 0
        elif self.travel_distance_meters < 0:
            errors['travel_distance_meters'] = _("Travel distance cannot be negative.")

        if errors:
            raise ValidationError(errors)

        # --- Contrôle de chevauchement dans le même TripDay ---
        if self.trip_day_id and self.start_time is not None and self.estimated_duration_minutes is not None:
            my_start, my_end = self._blocked_window()

            qs = self.trip_day.steps.exclude(pk=self.pk)  # autres steps du même jour
            for other in qs:
                # Calculer la fenêtre bloquée de l'autre
                o_travel = other.travel_duration_minutes or 0
                o_start_dt = datetime.combine(self.trip_day.date, other.start_time) - timedelta(minutes=o_travel)
                o_end_dt   = datetime.combine(self.trip_day.date, other.start_time) + timedelta(minutes=other.estimated_duration_minutes or 0)

                if self._overlap(my_start, my_end, o_start_dt, o_end_dt):
                    # Message explicite (ex: 12:00–15:00)
                    raise ValidationError({
                        'start_time': _(
                            "Time slot overlaps an existing step from %(s)s to %(e)s."
                        ) % {
                            's': o_start_dt.strftime("%H:%M"),
                            'e': o_end_dt.strftime("%H:%M")
                        }
                    })

    def save(self, *args, **kwargs):
        # Valider avant de calculer end_time
        self.full_clean()

        # Calcul d'end_time (activité uniquement)
        total_minutes = (self.estimated_duration_minutes or 0)
        if self.start_time is not None:
            full_dt = datetime.combine(datetime.today(), self.start_time) + timedelta(minutes=total_minutes)
            self.end_time = full_dt.time()
        else:
            self.end_time = None

        super().save(*args, **kwargs)
