# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/serialiser.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import serializers
from .models import Trip, TripDay, TripStep
from activities.serializers import ActivityListSerializer, EventSerializer
from activities.models import Activity, Event
from .services.address_service import get_or_create_address_cache

class TripStepSerializer(serializers.ModelSerializer):
    activity = ActivityListSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    activity_id = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all(), write_only=True, required=False)
    event_id = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), write_only=True, required=False)
    end_time = serializers.TimeField(read_only=True)  # ← ajouté ici

    class Meta:
        model = TripStep
        fields = [
            'id', 'trip_day', 'start_time', 'estimated_duration_minutes', 'end_time',
            'activity', 'event', 'notes',
            'activity_id', 'event_id'
        ]

    def create(self, validated_data):
        activity = validated_data.pop('activity_id', None)
        event = validated_data.pop('event_id', None)
        return TripStep.objects.create(activity=activity, event=event, **validated_data)

    def update(self, instance, validated_data):
        activity = validated_data.pop('activity_id', None)
        event = validated_data.pop('event_id', None)

        instance.activity = activity
        instance.event = event
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance




class TripDaySerializer(serializers.ModelSerializer):
    address = serializers.CharField(write_only=True, required=True)
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    steps = TripStepSerializer(many=True, read_only=True)

    class Meta:
        model = TripDay
        fields = ['id', 'trip', 'date', 'address', 'latitude', 'longitude', 'steps']

    def create(self, validated_data):
        address = validated_data.pop('address')
        address_cache = get_or_create_address_cache(address)
        trip_day = TripDay.objects.create(address_cache=address_cache, **validated_data)
        return trip_day

    def update(self, instance, validated_data):
        address = validated_data.pop('address', None)
        if address:
            address_cache = get_or_create_address_cache(address)
            instance.address_cache = address_cache

        instance.date = validated_data.get('date', instance.date)
        instance.save()
        return instance

class TripSerializer(serializers.ModelSerializer):
    days = TripDaySerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = ['id', 'user', 'title', 'start_date', 'end_date', 'created_at', 'updated_at', 'days']
        read_only_fields = ['user', 'created_at', 'updated_at']

class TripStepMoveSerializer(serializers.Serializer):
    start_time = serializers.TimeField()