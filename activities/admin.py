# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/activities/admin.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.contrib import admin

from .models.activity import Activity
from .models.event import Event
from .models.category import Category
from .models.promotion import Promotion

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "state", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("name", "city", "description")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_datetime", "end_datetime", "city", "is_public")
    list_filter = ("is_public", "category")
    search_fields = ("title", "description", "city")

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("title", "discount_type", "amount", "start_date", "end_date", "is_active")
    list_filter = ("discount_type", "is_active", "start_date", "end_date")
    search_fields = ("title", "description")

