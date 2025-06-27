# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/serializers.py
# Author : Morice
# ---------------------------------------------------------------------------



from ads.models import Advertisement
from activities.serializers import EventSerializer, ActivityDetailSerializer
from rest_framework import serializers
from .models import Partner, Advertisement, AdImpression, AdClick, AdConversion


# ─────────── PARTNER ────────────────────────

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = [
            "id",
            "name",
            "contact_email",
            "phone",
            "website",
            "contract_signed_date",
            "contract_type",
            "is_active",
            "created_at",
        ]

# ─────────── ADVERTISEMENT ──────────────────


class AdvertisementSerializer(serializers.ModelSerializer):
    # Partner en lecture complète
    partner = PartnerSerializer(read_only=True)
    # Partner ID en écriture
    partner_id = serializers.PrimaryKeyRelatedField(
        queryset=Partner.objects.all(), source='partner', write_only=True
    )

    # Event et Activity en lecture complète
    related_event_detail = EventSerializer(source="related_event", read_only=True)
    related_activity_detail = ActivityDetailSerializer(source="related_activity", read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "image",
            "link_url",
            "start_date",
            "end_date",
            "related_activity",
            "related_event",
            "related_activity_detail",  
            "related_event_detail",     
            "cpm_price",
            "cpc_price",
            "cpa_price",
            "forfait_price",
            "impressions_count",
            "clicks_count",
            "conversions_count",
            "created_at",
            "partner",
            "partner_id",
        ]


# ─────────── IMPRESSIONS / CLICS / CONVERSIONS ───────────

class AdImpressionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdImpression
        fields = [
            "id",
            "advertisement",
            "user",
            "timestamp",
        ]

class AdClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdClick
        fields = [
            "id",
            "advertisement",
            "user",
            "timestamp",
        ]

class AdConversionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdConversion
        fields = [
            "id",
            "advertisement",
            "user",
            "details",
            "timestamp",
        ]


