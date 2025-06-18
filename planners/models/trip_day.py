# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/models/trip_day.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from .trip import Trip
from .address_cache import AddressCache

class TripDay(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="days")
    date = models.DateField()
    address_cache = models.ForeignKey(AddressCache, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["date"]

    @property
    def latitude(self):
        return self.address_cache.latitude if self.address_cache else None

    @property
    def longitude(self):
        return self.address_cache.longitude if self.address_cache else None

    @property
    def address(self):
        return self.address_cache.address if self.address_cache else None
