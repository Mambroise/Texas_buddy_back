# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/signals.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TripDay

@receiver([post_save, post_delete], sender=TripDay)
def update_trip_dates(sender, instance, **kwargs):
    trip = instance.trip
    all_days = trip.days.order_by("date")

    if all_days.exists():
        trip.start_date = all_days.first().date
        trip.end_date = all_days.last().date
    else:
        # fallback logique, ex : ne rien faire ou reset
        trip.start_date = trip.end_date = None
    trip.save(update_fields=["start_date", "end_date"])
