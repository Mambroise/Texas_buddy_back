# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/models/activity.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from django.db.models import Q
from django.utils import timezone
from .category import Category
from ..service import generic_image_upload_to
from ..validators import validate_image

class Activity(models.Model):
    name = models.CharField(max_length=255, db_index=True)  # utile si ordering=name
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, db_index=True)  # (optionnel)
    state = models.CharField(max_length=100, default="Texas")
    zip_code = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    place_id = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    primary_category = models.ForeignKey(
        Category,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_for_activities",
        help_text="Category for markers in flutter UI etc.",
        # FK => index implicite
    )
    category = models.ManyToManyField(Category, related_name="activities")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    image = models.ImageField(upload_to=generic_image_upload_to, validators=[validate_image], blank=True, null=True)
    price = models.FloatField(blank=True, null=True, db_index=True)  # utile si ordering=price
    duration = models.DurationField(blank=True, null=True)
    average_rating = models.FloatField(default=0.0)
    staff_favorite = models.BooleanField(default=False)
    is_by_reservation = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # on l'utilise en filtre
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # Bounding box rapide pour la carte – seules les lignes “actives” et géolocalisées
            models.Index(
                fields=["latitude", "longitude"],
                name="act_lat_lon_active_idx",
                condition=Q(is_active=True, latitude__isnull=False, longitude__isnull=False),
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def current_promotion(self):
        now = timezone.now()
        return self.promotions.filter(is_active=True, start_date__lte=now, end_date__gte=now).first()
