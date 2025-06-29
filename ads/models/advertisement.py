# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/advertisement.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from django.core.exceptions import ValidationError

from .partner import Partner
from activities.models import Activity, Event


class Advertisement(models.Model):
    AD_FORMAT_CHOICES = [
        ("native", "Native Ad"),
        ("banner", "Banner"),
        ("interstitial", "Interstitial"),
        ("push", "Push Notification"),
        ("proximity", "Proximity Ad"),
        ("video_interstitial", "Video Interstitial"),  # tu peux ajouter ça si tu veux distinguer
    ]

    format = models.CharField(max_length=20, choices=AD_FORMAT_CHOICES, default="native")
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="ads/", blank=True, null=True)
    video = models.FileField(upload_to="ads/videos/", blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    link_url = models.URLField()
    start_date = models.DateField()
    end_date = models.DateField()
    related_activity = models.ForeignKey(
        Activity, null=True, blank=True, on_delete=models.SET_NULL, related_name="ads"
    )
    related_event = models.ForeignKey(
        Event, null=True, blank=True, on_delete=models.SET_NULL, related_name="ads"
    )
    cpm_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    cpc_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    cpa_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    forfait_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    impressions_count = models.PositiveIntegerField(default=0)
    clicks_count = models.PositiveIntegerField(default=0)
    conversions_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.related_activity and self.related_event:
            raise ValidationError("Une pub ne peut cibler qu'une activité OU un événement, pas les deux.")
        if self.format == "video_interstitial" and not (self.video or self.video_url):
            raise ValidationError("Une vidéo interstitielle doit avoir un fichier vidéo ou une URL.")
