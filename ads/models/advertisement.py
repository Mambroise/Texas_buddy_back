from django.db import models
from django.core.exceptions import ValidationError

from .contract import Contract
from activities.models import Activity, Event

class Advertisement(models.Model):
    AD_FORMAT_CHOICES = [
        ("native", "Native Ad"),
        ("banner", "Banner"),
        ("interstitial", "Interstitial"),
        ("push", "Push Notification"),
        ("proximity", "Proximity Ad"),
        ("video_interstitial", "Video Interstitial"),
    ]

    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="advertisements", null=True, blank=True
    )
    format = models.CharField(max_length=20, choices=AD_FORMAT_CHOICES, default="native")
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
    impressions_count = models.PositiveIntegerField(default=0)
    clicks_count = models.PositiveIntegerField(default=0)
    conversions_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        errors = {}

        # Only one target: either an activity or an event
        if self.related_activity and self.related_event:
            errors["related_activity"] = "An advertisement can target either an activity or an event, not both."
            errors["related_event"] = "An advertisement can target either an activity or an event, not both."

        # Video is mandatory for video interstitial format
        if self.format == "video_interstitial" and not (self.video or self.video_url):
            errors["video"] = "A video interstitial must have either a video file or a video URL."
            errors["video_url"] = "A video interstitial must have either a video file or a video URL."

        # Start and end dates consistency
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors["end_date"] = "End date must be later than start date."

        # Contract period validation (if a contract is attached)
        if self.contract:
            contract_start = self.contract.start_date
            contract_end = self.contract.end_date
            if self.start_date < contract_start:
                errors["start_date"] = f"Start date cannot be earlier than the contract start date ({contract_start})."
            if self.end_date > contract_end:
                errors["end_date"] = f"End date cannot be later than the contract end date ({contract_end})."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.title} ({self.contract})"

    def save(self, *args, **kwargs):
        # Enforce validation on save
        self.full_clean()
        super().save(*args, **kwargs)
