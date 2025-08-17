import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('texasbuddy')

# Lis les settings Django préfixés CELERY_*
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvre automatiquement les tasks dans <app>/tasks.py
app.autodiscover_tasks()

# Timezone Celery (tu peux aussi garder CELERY_TIMEZONE dans settings)
app.conf.timezone = 'Europe/Paris'
app.conf.enable_utc = True
