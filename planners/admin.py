# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/admin.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.contrib import admin

from .models import Trip, TripDay, TripStep, AddressCache


class TripInLine(admin.TabularInline):
    model = Trip
    extra = 1
    fields = ('title', 'start_date', 'end_date', 'adults', 'children')
    readonly_fields = ('created_at',)

class TripDayInLine(admin.TabularInline):
    model = TripDay
    extra = 0
    fields = ('date', 'address_cache',)

class TripStepInLine(admin.TabularInline):
    model = TripStep
    extra = 1
    fields = ('activity', 'event', 'start_time', 'estimated_duration_minutes', 'travel_mode', 'travel_duration_minutes', 'travel_distance_meters', 'notes', 'position')
    readonly_fields = ('end_time',)

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_date', 'end_date')
    search_fields = ('email', 'title',)
    inlines = [TripDayInLine]

@admin.register(TripDay)
class TripDayAdmin(admin.ModelAdmin):
    list_display = ('trip', 'date', 'address_cache')
    inlines = [TripStepInLine]

@admin.register(TripStep)
class TripStepAdmin(admin.ModelAdmin):
    list_display = ('trip_day', 'activity', 'event', 'start_time')
    ordering = ('trip_day', 'start_time')

@admin.register(AddressCache)
class AddressCacheAdmin(admin.ModelAdmin):
    readonly_fields = ('place_id', 'address', 'latitude', 'longitude', 'created_at')
