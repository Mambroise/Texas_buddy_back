# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/admin.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.contrib import admin
from .models import Partner, Advertisement, AdClick, AdImpression, AdConversion, AdInvoice
from .models.priority_ad import PriorityAd

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "contract_type", "is_active", "created_at")
    list_filter = ("contract_type", "is_active")
    search_fields = ("name", "contact_email")

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        "title", "partner", "start_date", "end_date", "related_activity", "related_event", "is_active_display",
        "impressions_count", "clicks_count", "conversions_count"
    )
    list_filter = ("start_date", "end_date", "partner__name")
    search_fields = ("title", "partner__name")
    readonly_fields = ("impressions_count", "clicks_count", "conversions_count")
    actions = ["activate_ads", "deactivate_ads"]

    def is_active_display(self, obj):
        from django.utils.timezone import now
        return obj.start_date <= now().date() <= obj.end_date
    is_active_display.boolean = True
    is_active_display.short_description = "Actif"

    def activate_ads(self, request, queryset):
        queryset.update(start_date="2024-01-01")  # à ajuster ou à ignorer
        self.message_user(request, "Pubs activées (attention aux dates réelles)")

    def deactivate_ads(self, request, queryset):
        from datetime import date, timedelta
        queryset.update(end_date=date.today() - timedelta(days=1))
        self.message_user(request, "Pubs désactivées")
    activate_ads.short_description = "Activer les publicités sélectionnées"
    deactivate_ads.short_description = "Désactiver les publicités sélectionnées"

@admin.register(AdClick)
class AdClickAdmin(admin.ModelAdmin):
    list_display = ("advertisement", "user", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("advertisement__title", "user__email")

@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):
    list_display = ("advertisement", "user", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("advertisement__title", "user__email")

@admin.register(AdConversion)
class AdConversionAdmin(admin.ModelAdmin):
    list_display = ("advertisement", "user", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("advertisement__title", "user__email")
    readonly_fields = ("details",)

@admin.register(PriorityAd)
class PriorityAdAdmin(admin.ModelAdmin):
    search_fields = ['advertisement__title', 'advertisement__partner__name']
    list_display = ['advertisement', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']

# invoices/admin.py-------------------------------------------------


@admin.register(AdInvoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partner",
        "period_start",
        "period_end",
        "generated_at",
        "total_amount",
        "tax_amount",
        "tax_rate",
        "currency",
        "is_paid",
    )
    list_filter = (
        "is_paid",
        "currency",
        "paid_at",
    )
    search_fields = (
        "partner__name",

    )
    date_hierarchy = "paid_at"

    actions = ["mark_as_paid"]

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status="PAID")
        self.message_user(request, f"{updated} facture(s) marquées comme payées.")
