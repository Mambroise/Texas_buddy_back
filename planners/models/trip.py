# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/models/trip.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from django.conf import settings

class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trips")
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def update_dates_from_days(self):
        days = self.days.order_by('date')
        if days.exists():
            self.start_date = days.first().date
            self.end_date = days.last().date
            self.save(update_fields=['start_date', 'end_date'])