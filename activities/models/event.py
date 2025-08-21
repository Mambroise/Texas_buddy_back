# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/activities/models/event.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from django.db.models import Q
from django.utils import timezone
from .category import Category
from ..service import generic_image_upload_to
from ..validators import validate_image

class Event(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    start_datetime = models.DateTimeField(db_index=True)  # on filtre/borne dessus
    end_datetime = models.DateTimeField(db_index=True)    # idem
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, db_index=True)  # (optionnel)
    state = models.CharField(max_length=100, default="Texas")
    zip_code = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    place_id = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    category = models.ManyToManyField(Category, related_name="events")
    primary_category = models.ForeignKey(
        Category,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_for_events",
        help_text="Category for markers in flutter UI etc.",
        # FK => index implicite
    )
    website = models.URLField(blank=True)
    image = models.ImageField(upload_to=generic_image_upload_to, validators=[validate_image], blank=True, null=True)
    price = models.FloatField(blank=True, null=True, db_index=True)
    duration = models.DurationField(blank=True, null=True)
    average_rating = models.FloatField(default=0.0)
    staff_favorite = models.BooleanField(default=False)
    is_national = models.BooleanField(default=False)
    has_updated_dates = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # Bounding box pour les évènements “publics” et géolocalisés
            models.Index(
                fields=["latitude", "longitude"],
                name="evt_lat_lon_public_idx",
                condition=Q(is_public=True, latitude__isnull=False, longitude__isnull=False),
            ),
            # Les deux colonnes ont chacune leur index (déjà ci-dessus) ; on évite __date (voir plus bas)
            # price/name ont déjà db_index si nécessaire
        ]

    def __str__(self):
        return self.name

    @property
    def current_promotion(self):
        now = timezone.now()
        return self.promotions.filter(
            is_active=True, start_date__lte=now, end_date__gte=now
        ).first()
