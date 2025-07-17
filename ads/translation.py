# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/translation.py
# Author : Morice
# ---------------------------------------------------------------------------


from modeltranslation.translator import register, TranslationOptions
from .models import Advertisement

@register(Advertisement)
class AdvertisementTranslationOptions(TranslationOptions):
    fields = ('title','push_message','ad_creative_content_text')