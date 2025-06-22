# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/activities/models/event.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from django.utils import timezone

from .category import Category
from ..service import generic_image_upload_to
from ..validators import validate_image

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    address = models.CharField(max_length=255, null=True,blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default="Texas")
    zip_code = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=255, null=True,blank=True)
    place_id = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    category = models.ManyToManyField(Category, related_name="events")
    website = models.URLField(blank=True)
    image = models.ImageField(upload_to=generic_image_upload_to,validators=[validate_image],blank=True,null=True)
    price = models.FloatField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    staff_favorite = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @property
    def current_promotion(self):
        now = timezone.now()
        return self.promotions.filter(
            is_active=True, start_date__lte=now, end_date__gte=now
        ).first()
