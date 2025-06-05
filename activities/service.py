# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/activities/admin.py
# Author : Morice
# ---------------------------------------------------------------------------


import os
import uuid
from django.utils.text import slugify
from datetime import datetime

def generic_image_upload_to(instance, filename):
    base, extension = os.path.splitext(filename)
    safe_name = slugify(base)
    date_path = datetime.now().strftime("%Y/%m/%d")
    unique_suffix = uuid.uuid4().hex[:8]

    # Dossier racine basé sur le nom du modèle
    model_name = instance.__class__.__name__.lower()  # e.g. "activity", "event"
    if model_name.endswith("y"):
        model_name = model_name[:-1] + "ies"  # activity -> activities
    else:
        model_name += "s"  # event -> events

    return f'{model_name}/{date_path}/{safe_name}_{unique_suffix}{extension}'