# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/serializers.py
# Author : Morice
# ---------------------------------------------------------------------------



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
    partner = PartnerSerializer(read_only=True)
    partner_id = serializers.PrimaryKeyRelatedField(
        queryset=Partner.objects.all(), source='partner', write_only=True
    )

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
            "cpm_price",
            "cpc_price",
            "cpa_price",
            "forfait_price",
            "impressions_count",
            "clicks_count",
            "conversions_count",
            "created_at",
            "partner",
            "partner_id",  # pour POST/PUT
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

class AdvertisementSerializer(serializers.ModelSerializer):
    partner_name = serializers.CharField(source="partner.name", read_only=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'image', 'link_url', 'format', 'partner_name',
            'related_activity', 'related_event', 'start_date', 'end_date', 'type'
        ]

    def get_type(self, obj):
        if obj.related_activity:
            return "activity"
        if obj.related_event:
            return "event"
        return "other"
