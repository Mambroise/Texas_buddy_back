# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : planners/serializers.py
# Author : Morice
# ---------------------------------------------------------------------------

from datetime import datetime, timedelta

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Trip, TripDay, TripStep, AddressCache
from activities.models import Activity, Event
from activities.serializers import ActivityListSerializer, EventDetailSerializer


class TripStepSerializer(serializers.ModelSerializer):
    # Read-only expanded objects
    activity = ActivityListSerializer(read_only=True)
    event = EventDetailSerializer(read_only=True)

    # Write-only PK inputs → mappés vers les FK réelles du modèle
    activity_id = serializers.PrimaryKeyRelatedField(
        source='activity',
        queryset=Activity.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    event_id = serializers.PrimaryKeyRelatedField(
        source='event',
        queryset=Event.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    end_time = serializers.TimeField(read_only=True)

    class Meta:
        model = TripStep
        fields = [
            'id', 'trip_day', 'start_time', 'estimated_duration_minutes', 'end_time',
            'activity', 'event', 'notes',
            'activity_id', 'event_id',
            'travel_mode', 'travel_duration_minutes', 'travel_distance_meters',
        ]

    # --- Helpers internes ---------------------------------------------------
    def _blocked_window_preview(self, trip_day, start_time, est_min, travel_min):
        day = getattr(trip_day, "date", datetime.today().date())
        start_dt = datetime.combine(day, start_time) - timedelta(minutes=(travel_min or 0))
        end_dt   = datetime.combine(day, start_time) + timedelta(minutes=(est_min or 0))
        return start_dt, end_dt

    # --- Validation ---------------------------------------------------------
    def validate(self, attrs):
        # Règle de présence: activity XOR event (en création),
        # en update on autorise l'absence si déjà présent sur l'instance.
        act = attrs.get('activity', getattr(self.instance, 'activity', None))
        evt = attrs.get('event', getattr(self.instance, 'event', None))

        if self.instance is None:
            if not act and not evt:
                raise serializers.ValidationError({
                    'non_field_errors': _("Either activity_id or event_id is required.")
                })
        if act and evt:
            raise serializers.ValidationError({
                'non_field_errors': _("Provide either activity_id OR event_id, not both.")
            })

        # Anti-overlap (fenêtre bloquée: [start - travel ; start + estimated])
        trip_day = attrs.get('trip_day') or getattr(self.instance, 'trip_day', None)
        start_time = attrs.get('start_time') or getattr(self.instance, 'start_time', None)
        if 'estimated_duration_minutes' in attrs:
            est_min = attrs.get('estimated_duration_minutes')
        else:
            est_min = getattr(self.instance, 'estimated_duration_minutes', None)

        if 'travel_duration_minutes' in attrs:
            travel_min = attrs.get('travel_duration_minutes') or 0
        else:
            travel_min = getattr(self.instance, 'travel_duration_minutes', 0) or 0

        if trip_day and start_time is not None and est_min is not None:
            my_s, my_e = self._blocked_window_preview(trip_day, start_time, est_min, travel_min)

            qs = trip_day.steps.all()
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            for other in qs:
                o_s = datetime.combine(trip_day.date, other.start_time) - timedelta(minutes=(other.travel_duration_minutes or 0))
                o_e = datetime.combine(trip_day.date, other.start_time) + timedelta(minutes=(other.estimated_duration_minutes or 0))
                if not (my_e <= o_s or o_e <= my_s):
                    raise serializers.ValidationError({
                        'start_time': _(
                            "Overlaps with another step (%(s)s–%(e)s)."
                        ) % {'s': o_s.strftime("%H:%M"), 'e': o_e.strftime("%H:%M")}
                    })

        return attrs

    # Optionnel: robustesse si un client envoie encore 'activity_id'/'event_id'
    # sans 'source' ou souhaite les mettre à None: déjà géré via fields ci-dessus.
    # Pas besoin d'override create()/update().


class TripDaySerializer(serializers.ModelSerializer):
    # ⬇️ Composé dynamiquement: "name + formatted_address"
    address   = serializers.SerializerMethodField(read_only=True)
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

    def get_address(self, obj):
        ac = getattr(obj, 'address_cache', None)
        if not ac:
            return None
        name = (getattr(ac, 'name', '') or '').strip()
        formatted = (getattr(ac, 'formatted_address', '') or '').strip()

        # si les deux existent, évite la duplication (ex: le name déjà inclus dans formatted)
        if name and formatted:
            if name.lower() in formatted.lower():
                return formatted
            return f"{name} {formatted}"

        return name or formatted or None

    def validate(self, attrs):
        if 'address_cache' in attrs:
            return attrs
        place_id = attrs.pop('place_id', None)
        if place_id:
            try:
                attrs['address_cache'] = AddressCache.objects.get(place_id=place_id)
            except AddressCache.DoesNotExist:
                raise serializers.ValidationError({'place_id': 'Unknown place_id in AddressCache.'})
        return attrs

    def update(self, instance, validated_data):
        if 'address_cache' in validated_data and validated_data['address_cache'] is None:
            instance.address_cache = None
        else:
            ac = validated_data.get('address_cache')
            if ac is not None:
                instance.address_cache = ac

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
        new_start = validated_data.get('start_date', instance.start_date)
        new_end   = validated_data.get('end_date',   instance.end_date)

        if new_start and new_end and new_start > new_end:
            raise ValidationError({'end_date': "Must be >= start_date"})

        for k in ('title', 'adults', 'children'):
            if k in validated_data:
                setattr(instance, k, validated_data[k])

        range_changed = (new_start != instance.start_date) or (new_end != instance.end_date)
        if new_start and new_end and range_changed:
            existing_dates = set(instance.days.values_list('date', flat=True))
            for d in _daterange(new_start, new_end):
                if d not in existing_dates:
                    TripDay.objects.create(trip=instance, date=d)

            outside = instance.days.exclude(date__gte=new_start, date__lte=new_end)
            if outside.filter(steps__isnull=False).exists():
                raise ValidationError({
                    'date_range': "Cannot shrink date range: some out-of-range days have steps."
                })
            outside.delete()

            instance.update_dates_from_days()
        else:
            instance.save(update_fields=['title', 'adults', 'children'])

        return instance


class TripStepMoveSerializer(serializers.Serializer):
    start_time = serializers.TimeField()


# Serializer coming from flutter for tripDay address update after lookup
class TripDayAddressUpdateSerializer(serializers.Serializer):
    trip_day_id = serializers.IntegerField()
    address = serializers.CharField(max_length=512)
    place_id = serializers.CharField(max_length=255)
