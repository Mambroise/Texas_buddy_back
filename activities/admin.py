# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/activities/admin.py
# Author : Morice
# ---------------------------------------------------------------------------


# texasbuddy/activities/admin.py
from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from .models.activity import Activity
from .models.event import Event
from .models.category import Category
from .models.promotion import Promotion


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    readonly_fields = ('id',)
    search_fields = ("name",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "place_id", "city", "state", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("name", "city", "description")


# --- Filtre pratique pour ne voir que ceux à remettre à jour ---
class NeedsUpdateFilter(admin.SimpleListFilter):
    title = _("Dates à mettre à jour")
    parameter_name = "needs_update"

    def lookups(self, request, model_admin):
        return [
            ("yes", _("À mettre à jour (has_updated_dates = False)")),
            ("no",  _("À jour (has_updated_dates = True)")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(has_updated_dates=False)
        if self.value() == "no":
            return queryset.filter(has_updated_dates=True)
        return queryset


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name", "start_datetime", "end_datetime", "place_id",
        "city", "is_public", "has_updated_dates",
    )
    list_filter = ("is_public", "category", NeedsUpdateFilter)  # ou simplement: ("is_public", "category", "has_updated_dates")
    search_fields = ("name", "description", "city")

    # ---- Action pour la sélection ----
    @admin.action(description=_("Mettre 'has_updated_dates' à False pour la sélection"))
    def reset_has_updated_dates(self, request, queryset):
        updated = queryset.update(has_updated_dates=False)
        self.message_user(
            request,
            _("%(count)d évènement(s) mis à jour.") % {"count": updated},
            level=messages.SUCCESS,
        )

    actions = ["reset_has_updated_dates"]

    # ---- Bouton global "Reset ALL" dans la barre d'outils ----
    change_list_template = "admin/activities/event/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "reset-all-dates/",
                self.admin_site.admin_view(self.reset_all_dates_view),
                name="activities_event_reset_all_dates",
            )
        ]
        return custom + urls

    def reset_all_dates_view(self, request):
        updated = Event.objects.update(has_updated_dates=False)
        self.message_user(
            request,
            _("%(count)d évènement(s) mis à jour (Reset ALL).") % {"count": updated},
            level=messages.SUCCESS,
        )
        return redirect(reverse("admin:activities_event_changelist"))


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("title", "discount_type", "amount", "start_date", "end_date", "is_active")
    list_filter = ("discount_type", "is_active", "start_date", "end_date")
    search_fields = ("title", "description")


