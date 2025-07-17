# ---------------------------------------------------------------------------
#                            TEXAS BUDDY  ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/advertisement.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.conf import settings
from django.db import models
from activities.models import Activity, Event  

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.CASCADE, related_name="reviews")
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('user', 'activity'),
            ('user', 'event'),
        )

    def __str__(self):
        target = self.activity or self.event
        return f"{self.user.email} -> {target} ({self.rating})"
