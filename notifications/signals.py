# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/notifications/signals.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from .services.email_service import send_credentials_email

User = get_user_model()

@receiver(post_save, sender=User)
def send_user_credentials(sender, instance, created, **kwargs):
    if created:
        send_credentials_email(instance)
