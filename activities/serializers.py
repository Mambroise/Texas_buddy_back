# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/sirializers.py
# Author : Morice
# ---------------------------------------------------------------------------

from rest_framework import serializers
from .models import Activity, Event, Category, Promotion

# -- Petits serializers de base ------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'description']

class PromotionLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['title', 'discount_type', 'amount', 'end_date']

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = [
            'id', 'title', 'description', 'discount_type', 'amount',
            'start_date', 'end_date', 'is_active'
        ]

# -- Helpers communs -----------------------------------------------------------

def _reference_date_from_request(request):
    from datetime import datetime
    from django.utils import timezone
    date_str = request.query_params.get('date') if request else None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()
    except ValueError:
        return timezone.now().date()

# -- LISTE: utilisés sur la carte (Nearby) ------------------------------------

class ActivityListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    primary_category = CategorySerializer(read_only=True)
    has_promotion = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    matches_user_interest = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id", "name", "place_id", "latitude", "longitude",
            "category", "primary_category",
            "staff_favorite", "price",
            "has_promotion", "duration",
            "type","matches_user_interest",
        ]

    def get_type(self, obj): return "activity"

    def get_matches_user_interest(self, obj):
        interest_ids = self.context.get("user_interest_ids") or set()
        primary_id = getattr(obj, "primary_category_id", None)
        return bool(primary_id and primary_id in interest_ids)

    def get_has_promotion(self, obj):
        ref_date = _reference_date_from_request(self.context.get('request'))
        return obj.promotions.filter(
            is_active=True,
            start_date__lte=ref_date,
            end_date__gte=ref_date
        ).exists()


class EventListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    primary_category = CategorySerializer(read_only=True)
    has_promotion = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    matches_user_interest = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id", "name", "place_id", "latitude", "longitude",
            "start_datetime", "end_datetime",
            "category", "primary_category",
            "staff_favorite", "price",
            "has_promotion", "type",
            "matches_user_interest",
        ]

    def get_type(self, obj): return "event"

    def get_matches_user_interest(self, obj):
        interest_ids = self.context.get("user_interest_ids") or set()
        primary_id = getattr(obj, "primary_category_id", None)
        return bool(primary_id and primary_id in interest_ids)

    def get_has_promotion(self, obj):
        ref_date = _reference_date_from_request(self.context.get('request'))
        return obj.promotions.filter(
            is_active=True,
            start_date__lte=ref_date,
            end_date__gte=ref_date
        ).exists()


# -- DÉTAIL: ouverts au double-tap / tap sur le label --------------------------

class ActivityDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    primary_category = CategorySerializer(read_only=True)
    # Si le modèle expose une FK/OneToOne `current_promotion`, on peut garder read_only=True.
    # Sinon, on la calcule dynamiquement avec un SerializerMethodField (voir Event).
    current_promotion = PromotionSerializer(read_only=True)

    class Meta:
        model = Activity
        fields = [
            "id", "name", "description",
            "category", "primary_category",
            "address", "city", "state", "zip_code",
            "place_id", "latitude", "longitude",
            "image", "website", "phone", "email",
            "price", "duration", "is_by_reservation", "staff_favorite", "is_active", "created_at",
            "current_promotion",
        ]

class EventDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    primary_category = CategorySerializer(read_only=True)
    promotions = PromotionSerializer(many=True, read_only=True)
    current_promotion = serializers.SerializerMethodField()
    has_promotion = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id", "name", "description",
            "start_datetime", "end_datetime",
            "location", "city", "state",
            "place_id", "latitude", "longitude",
            "category", "primary_category", "website",
            "image", "price", "duration", "is_by_reservation",
            "staff_favorite", "is_public", "created_at",
            "promotions", "current_promotion", "has_promotion",
        ]

    # Si le modèle expose déjà une propriété/annotation `current_promotion`,
    # on la renvoie en "plein" (pas lite) pour l’écran de détail.
    def get_current_promotion(self, obj):
        promo = getattr(obj, "current_promotion", None)
        return PromotionSerializer(promo).data if promo else None

    def get_has_promotion(self, obj):
        ref_date = _reference_date_from_request(self.context.get('request'))
        return obj.promotions.filter(
            is_active=True,
            start_date__lte=ref_date,
            end_date__gte=ref_date
        ).exists()