from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg

from community.models import Review
from activities.models import Activity, Event

def _update_average_for_activity(activity_id):
    avg = Review.objects.filter(activity_id=activity_id).aggregate(avg=Avg('rating'))['avg'] or 0.0
    Activity.objects.filter(id=activity_id).update(average_rating=avg)

def _update_average_for_event(event_id):
    avg = Review.objects.filter(event_id=event_id).aggregate(avg=Avg('rating'))['avg'] or 0.0
    Event.objects.filter(id=event_id).update(average_rating=avg)

@receiver(post_save, sender=Review)
def update_average_on_save(sender, instance, **kwargs):
    if instance.activity_id:
        _update_average_for_activity(instance.activity_id)
    if instance.event_id:
        _update_average_for_event(instance.event_id)

@receiver(post_delete, sender=Review)
def update_average_on_delete(sender, instance, **kwargs):
    if instance.activity_id:
        _update_average_for_activity(instance.activity_id)
    if instance.event_id:
        _update_average_for_event(instance.event_id)
