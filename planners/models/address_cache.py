# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/services/address_cache_service.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils import timezone

class AddressCache(models.Model):
    place_id = models.CharField(max_length=128, unique=True, null=True, blank=True)    # Google place_id
    name = models.CharField(max_length=256, null=True, blank=True)  # ex: "Central Park"
    formatted_address = models.TextField(null=True, blank=True)

    # Coords
    lat = models.FloatField()
    lng = models.FloatField()

    # Localisation normalisée
    city = models.CharField(max_length=128, db_index=True, null=True)          # ex: "Dallas"
    state_code = models.CharField(max_length=8, db_index=True, null=True)       # ex: "TX"
    country_code = models.CharField(max_length=2, db_index=True, default="US")

    # i18n & source
    language = models.CharField(max_length=5, default="en")          # "fr", "en", "es"
    source = models.CharField(max_length=16, default="google")       # "google", "osm", etc.
    components = models.JSONField(default=dict, blank=True)          # adresse décomposée

    # Recherche texte
    search_vector = SearchVectorField(null=True)

    # Cache mgmt
    created_at = models.DateTimeField(auto_now_add=True)
    refreshed_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    hit_count = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
            models.Index(fields=["language"]),
            models.Index(fields=["city"]),
            models.Index(fields=["state_code"]),
            models.Index(fields=["country_code"]),
        ]

    def __str__(self):
        return f"{self.name} — {self.formatted_address}"
