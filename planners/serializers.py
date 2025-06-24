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

class TripStepSerializer(serializers.ModelSerializer):
    activity = ActivityListSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    activity_id = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all(), write_only=True, required=False)
    event_id = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), write_only=True, required=False)
    end_time = serializers.TimeField(read_only=True)

    class Meta:
        model = TripStep
        fields = [
            'id', 'trip_day', 'start_time', 'estimated_duration_minutes', 'end_time',
            'activity', 'event', 'notes',
            'activity_id', 'event_id',
            'travel_mode', 'travel_duration_minutes', 'travel_distance_meters'
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
    address = serializers.CharField(source='address_cache.address', read_only=True)
    latitude = serializers.FloatField(source='address_cache.latitude', read_only=True)
    longitude = serializers.FloatField(source='address_cache.longitude', read_only=True)
    steps = TripStepSerializer(many=True, read_only=True)

    class Meta:
        model = TripDay
        fields = ['id', 'trip', 'date', 'address', 'latitude', 'longitude', 'steps']
        

class TripSerializer(serializers.ModelSerializer):
    days = TripDaySerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = ['id', 'user', 'title', 'start_date', 'end_date', 'created_at', 'updated_at', 'days']
        read_only_fields = ['user', 'created_at', 'updated_at']

class TripStepMoveSerializer(serializers.Serializer):
    start_time = serializers.TimeField()

# Serializer comming from flutter for tripDay address update after lookup
class TripDayAddressUpdateSerializer(serializers.Serializer):
    trip_day_id = serializers.IntegerField()
    address = serializers.CharField(max_length=512)
    place_id = serializers.CharField(max_length=255)