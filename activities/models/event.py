# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/activities/models/event.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from .category import Category
from ..service import generic_image_upload_to
from ..validators import validate_image

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default="Texas")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    category = models.ManyToManyField(Category, related_name="events")
    website = models.URLField(blank=True)
    image = models.ImageField(upload_to=generic_image_upload_to,validators=[validate_image],blank=True,null=True)
    price = models.FloatField(blank=True, null=True)
    staff_favorite = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
