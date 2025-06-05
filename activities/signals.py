# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/activities/signals.py
# Author : Morice
# ---------------------------------------------------------------------------


import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models.activity import Activity
from .models.event import Event

# ========= Series of functions to delete old images from serveur when deleted or updated =======
def delete_old_file(fieldfile):
    if fieldfile and fieldfile.name:
        file_path = fieldfile.path
        if os.path.isfile(file_path):
            os.remove(file_path)

@receiver(pre_save, sender=Activity)
def auto_delete_old_activity_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_instance = Activity.objects.get(pk=instance.pk)
    except Activity.DoesNotExist:
        return

    if old_instance.image and old_instance.image != instance.image:
        delete_old_file(old_instance.image)

@receiver(post_delete, sender=Activity)
def auto_delete_activity_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        delete_old_file(instance.image)


@receiver(pre_save, sender=Event)
def auto_delete_old_event_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_instance = Event.objects.get(pk=instance.pk)
    except Event.DoesNotExist:
        return

    if old_instance.image and old_instance.image != instance.image:
        delete_old_file(old_instance.image)

@receiver(post_delete, sender=Event)
def auto_delete_event_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        delete_old_file(instance.image)
# ======================================== end ============================