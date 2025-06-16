# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/translation.py
# Author : Morice
# ---------------------------------------------------------------------------


from modeltranslation.translator import register, TranslationOptions
from .models import Activity, Category, Event, Promotion

@register(Activity)
class ActivityTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'location')

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Event)
class EventTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'location')

@register(Promotion)
class PromotionTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

