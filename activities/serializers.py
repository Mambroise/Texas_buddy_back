# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/sirializers.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import serializers
from .models import Activity,Event,Category,Promotion


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'description']


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = [
            'id', 'title', 'description', 'discount_type', 'amount',
            'start_date', 'end_date', 'is_active',
            'activity', 'event'
        ]

class ActivitySerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)  # car c'est un ManyToManyField
    promotions = PromotionSerializer(source='promotions', many=True, read_only=True)

    class Meta:
        model = Activity
        fields = [
            "id", "name", "description", "category",
            "address", "city", "state", "zip_code", "latitude", "longitude",
            "image", "website", "phone", "email",
            "price", "staff_favorite", "is_active", "created_at",
            "promotions"
        ]


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    promotions = PromotionSerializer(source='promotions', many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "description", "start_datetime", "end_datetime",
            "location", "city", "state", "latitude", "longitude",
            "category", "website", "image", "price", "staff_favorite",
            "is_public", "created_at", "promotions"
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'description']
