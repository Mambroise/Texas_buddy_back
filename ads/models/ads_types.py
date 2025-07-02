# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/ads_types.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from django.conf import settings

from ads.manager import AdLogQuerySet
from .advertisement import Advertisement


class AdImpression(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = AdLogQuerySet.as_manager()

class AdClick(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = AdLogQuerySet.as_manager()

class AdConversion(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = AdLogQuerySet.as_manager()