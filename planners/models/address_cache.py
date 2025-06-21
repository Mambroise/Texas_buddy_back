# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/models/address_cache.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models

class AddressCache(models.Model):
    place_id = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=512)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address} ({self.latitude}, {self.longitude})"
