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
    fields = ('date',) # 'address_cache'

class TripStepInLine(admin.TabularInline):
    model = TripStep
    extra = 1
    fields = ('activity', 'event', 'start_time', 'estimated_duration_minutes', 'travel_mode', 'travel_duration_minutes', 'travel_distance_meters', 'notes', 'position')
    readonly_fields = ('end_time',)

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'start_date', 'end_date')
    search_fields = ('email', 'title',)
    inlines = [TripDayInLine]

@admin.register(TripDay)
class TripDayAdmin(admin.ModelAdmin):
    list_display = ('trip', 'date')  # 'address_cache'
    inlines = [TripStepInLine]

@admin.register(TripStep)
class TripStepAdmin(admin.ModelAdmin):
    list_display = ('trip_day', 'activity', 'event', 'start_time')
    ordering = ('trip_day', 'start_time')

@admin.register(AddressCache)
class AddressCacheAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'formatted_address', 'city', 'state_code', 'country_code', 'place_id', 'lat', 'lng', 'source', 'language', 'hit_count', 'last_used_at')
    search_fields = ('name', 'formatted_address', 'city', 'state_code', 'country_code')
    readonly_fields = ('created_at', 'refreshed_at', 'expires_at', 'hit_count', 'last_used_at')
    list_filter = ('country_code', 'state_code', 'city', 'source', 'language')
    ordering = ('-last_used_at',)
