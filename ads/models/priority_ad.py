# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/priority_ad.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from ads.models.advertisement import Advertisement

class PriorityAd(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name="priority_entries")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PriorityAd: {self.advertisement.title} ({'active' if self.is_active else 'inactive'})"
