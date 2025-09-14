# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/serializers.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import serializers
from .models import Trip, TripDay, TripStep
from activities.serializers import ActivityListSerializer, EventDetailSerializer
from activities.models import Activity, Event
from datetime import timedelta
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Trip, TripDay, TripStep, AddressCache


class TripStepSerializer(serializers.ModelSerializer):
    activity = ActivityListSerializer(read_only=True)
    event = EventDetailSerializer(read_only=True)
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
    # --- Sortie JSON attendue par le front (back-compat) ---
    address   = serializers.CharField(source='address_cache.formatted_address', read_only=True)
    latitude  = serializers.FloatField(source='address_cache.lat', read_only=True)
    longitude = serializers.FloatField(source='address_cache.lng', read_only=True)

    steps = TripStepSerializer(many=True, read_only=True)

    # --- Entrées PATCH ---
    address_cache_id = serializers.PrimaryKeyRelatedField(
        source='address_cache',
        queryset=AddressCache.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    place_id = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = TripDay
        fields = [
            'id', 'trip', 'date',
            'address', 'latitude', 'longitude',
            'steps',
            'address_cache_id', 'place_id',
        ]
        read_only_fields = ['trip']

    def validate(self, attrs):
        # Si address_cache_id a été fourni, DRF l’a déjà mappé → rien à faire
        if 'address_cache' in attrs:
            return attrs
        # Sinon on accepte place_id (cas Google)
        place_id = attrs.pop('place_id', None)
        if place_id:
            try:
                attrs['address_cache'] = AddressCache.objects.get(place_id=place_id)
            except AddressCache.DoesNotExist:
                raise serializers.ValidationError({'place_id': 'Unknown place_id in AddressCache.'})
        return attrs

    def update(self, instance, validated_data):
        # Mise à jour de l'address_cache si présent
        if 'address_cache' in validated_data and validated_data['address_cache'] is None:
            instance.address_cache = None
        else:
            ac = validated_data.get('address_cache')
            if ac is not None:
                instance.address_cache = ac

        # Autres champs patchables (ex. date)
        for f, v in validated_data.items():
            if f not in ('address_cache',):
                setattr(instance, f, v)

        instance.save()
        return instance
        

def _daterange(d1, d2):
    cur = d1
    while cur <= d2:
        yield cur
        cur += timedelta(days=1)

class TripSerializer(serializers.ModelSerializer):
    days = TripDaySerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id', 'user', 'title', 'start_date', 'end_date',
            'adults', 'children', 'created_at', 'updated_at', 'days'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def update(self, instance: Trip, validated_data):
        # Récupère nouvelles bornes ou valeurs courantes
        new_start = validated_data.get('start_date', instance.start_date)
        new_end   = validated_data.get('end_date',   instance.end_date)

        # Sanity check si dates présentes
        if new_start and new_end and new_start > new_end:
            raise ValidationError({'end_date': "Must be >= start_date"})

        # 1) MAJ des champs simples
        for k in ('title', 'adults', 'children'):
            if k in validated_data:
                setattr(instance, k, validated_data[k])

        # 2) Si on change l’intervalle, sync des TripDay
        range_changed = (new_start != instance.start_date) or (new_end != instance.end_date)
        if new_start and new_end and range_changed:
            # a) Ajouter les jours manquants si on étend
            existing_dates = set(instance.days.values_list('date', flat=True))
            for d in _daterange(new_start, new_end):
                if d not in existing_dates:
                    TripDay.objects.create(trip=instance, date=d)

            # b) Supprimer les jours hors plage si on rétrécit
            outside = instance.days.exclude(date__gte=new_start, date__lte=new_end)
            # Si certains jours ont des steps → bloquer (ou change ici pour ‘soft delete/archiver’)
            if outside.filter(steps__isnull=False).exists():
                raise ValidationError({
                    'date_range': "Cannot shrink date range: some out-of-range days have steps."
                })
            outside.delete()

            # c) Met à jour les bornes d’après les days existants (source de vérité)
            instance.update_dates_from_days()
        else:
            # Plage inchangée → on enregistre simplement
            instance.save(update_fields=['title', 'adults', 'children'])

        return instance

class TripStepMoveSerializer(serializers.Serializer):
    start_time = serializers.TimeField()

# Serializer comming from flutter for tripDay address update after lookup
class TripDayAddressUpdateSerializer(serializers.Serializer):
    trip_day_id = serializers.IntegerField()
    address = serializers.CharField(max_length=512)
    place_id = serializers.CharField(max_length=255)
    