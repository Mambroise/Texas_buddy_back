from django.contrib import admin

from .models import Trip, TripDay, TripStep


class TripInLine(admin.TabularInline):
    model = Trip
    extra = 1
    fields = ('title', 'start_date', 'end_date', 'created_at',)

class TripDayInLine(admin.TabularInline):
    model = TripDay
    extra = 0
    fields = ('date', 'location_name',)

class TripStepInLine(admin.TabularInline):
    model = TripStep
    extra = 1
    fields = ('activity', 'event', 'start_time', 'estimated_duration_minutes', 'travel_time_minutes', 'end_time', 'notes', 'position')
