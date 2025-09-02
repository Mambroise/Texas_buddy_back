# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/serializers.py
# Author : Morice
# ---------------------------------------------------------------------------


from .models import Advertisement, Partner, AdInvoice
from activities.serializers import EventDetailSerializer, ActivityDetailSerializer
from rest_framework import serializers
from .models import Partner, Advertisement, AdImpression, AdClick, AdConversion


# ─────────── PARTNER ────────────────────────

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = [
            "id",
            "name",
            "legal_name",
            "contact_person",
            "contact_email",
            "address",
            "zipcode",
            "city",
            "state",
            "country",
            "phone",
            "website",
            "tax_id_number",
            "is_active",
            "created_at",
            "updated_at",
        ]

# ─────────── ADVERTISEMENT ──────────────────


class AdvertisementSerializer(serializers.ModelSerializer):
    # This commented part goes with the commented fields below
    # Partner in full display
    # partner = PartnerSerializer(read_only=True)
    # Partner ID en écriture
    # partner_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Partner.objects.all(), source='partner', write_only=True
    # )

    # Event et Activity en lecture complète
    related_event_detail = EventDetailSerializer(source="related_event", read_only=True)
    related_activity_detail = ActivityDetailSerializer(source="related_activity", read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "io_reference_number",
            "contract",
            "campaign_type",
            "format",
            "title",
            "ad_creative_content_text",
            "image",
            "video",
            "video_url",
            "link_url",
            "start_date",
            "end_date",
            "status",
            "related_activity",
            "related_event",
            "related_event_detail",
            "related_activity_detail",
            # "partner",
            # "partner_id",
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


# invoices/serializers------------------------------------------------------------


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdInvoice
        fields = "__all__"