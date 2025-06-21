# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/models/trip.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from django.conf import settings

from django.apps import apps

from datetime import timedelta

class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trips")
    title = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def create_trip_days(self):
        TripDay = apps.get_model('planners', 'TripDay') 
        current_date = self.start_date
        while current_date <= self.end_date:
            TripDay.objects.create(trip=self, date=current_date)
            current_date += timedelta(days=1)

    def update_dates_from_days(self):
        all_days = self.days.order_by('date')
        if all_days.exists():
            self.start_date = all_days.first().date
            self.end_date = all_days.last().date
            self.save(update_fields=['start_date', 'end_date'])
