# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/sirializers.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import serializers
from .models import Activity,Event,Category,Promotion
from users.models.user import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'description']


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = [
            'id', 'title', 'description', 'discount_type', 'amount',
            'start_date', 'end_date', 'is_active'
        ]


# --- Liste : utilisé sur la carte ---
class ActivityListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    primary_category = CategorySerializer(read_only=True) 
    has_promotion = serializers.SerializerMethodField()
    distance = serializers.FloatField(read_only=True)


    class Meta:
        model = Activity
        fields = [
            "id", "name", "place_id", "latitude", "longitude", "category", "primary_category", 
            "staff_favorite", "price", "has_promotion", "distance",
        ]

    
    def get_has_promotion(self, obj):
        request = self.context.get('request')
        date_str = request.query_params.get('date') if request else None

        from datetime import datetime
        from django.utils import timezone

        try:
            reference_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()
        except ValueError:
            reference_date = timezone.now().date()

        promotion = obj.promotions.filter(
            is_active=True,
            start_date__lte=reference_date,
            end_date__gte=reference_date
        ).first()

        return promotion is not None
    
    


# --- Détail : utilisé lorsqu'on clique sur une activité ---
class ActivityDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    primary_category = CategorySerializer(read_only=True) 
    current_promotion = PromotionSerializer(read_only=True)


    class Meta:
        model = Activity
        fields = [
            "id", "name", "description", "category", "primary_category", 
            "address", "city", "state", "zip_code", "place_id", "latitude", "longitude",
            "image", "website", "phone", "email",
            "price", "duration", "staff_favorite", "is_active", "created_at",
            "current_promotion", 
        ]


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    primary_category = CategorySerializer(read_only=True) 
    promotions = PromotionSerializer(many=True, read_only=True)
    current_promotion = serializers.SerializerMethodField()
    has_promotion = serializers.SerializerMethodField()
    distance = serializers.FloatField(read_only=True)


    class Meta:
        model = Event
        fields = [
            "id", "name", "description", "start_datetime", "end_datetime",
            "location", "city", "state", "place_id", "latitude", "longitude",
            "category", "primary_category", "website", "image", "price", "duration", "staff_favorite",
            "is_public", "created_at",
            "promotions", "current_promotion", "has_promotion", "distance", 
        ]

    
    def get_current_promotion(self, obj):
        promotion = obj.current_promotion
        if promotion:
            return PromotionLiteSerializer(promotion).data
        return None

    def get_has_promotion(self, obj):
        request = self.context.get('request')
        date_str = request.query_params.get('date') if request else None

        from datetime import datetime
        from django.utils import timezone

        try:
            reference_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()
        except ValueError:
            reference_date = timezone.now().date()

        return obj.promotions.filter(
            is_active=True,
            start_date__lte=reference_date,
            end_date__gte=reference_date
        ).exists()


class PromotionLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['title', 'discount_type', 'amount', 'end_date']
