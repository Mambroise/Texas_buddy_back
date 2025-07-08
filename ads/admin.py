# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/admin.py
# Author : Morice
# ---------------------------------------------------------------------------

import datetime
from datetime import datetime
from django.contrib import admin
from .models import (
    Partner, Advertisement, AdClick, AdImpression, AdConversion, AdInvoice, Contract
)
from django.contrib import messages
from .models.priority_ad import PriorityAd
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Q


from .models import Advertisement, Contract
from .models.ads_types import AdImpression, AdClick, AdConversion
from .services.email_service import send_invoice_email



admin.site.site_header = "Texas Buddy Administration"
admin.site.site_title = "Texas Buddy Admin"
admin.site.index_title = "Welcome to Texas Buddy Admin Panel"

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "legal_name", "contact_email", "tax_id_number", "phone", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("legal_name", "contact_person", "tax_id_number", "contact_email")


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "partner", "contract_reference", "start_date", "duration_months",
        "signed_date", "auto_renew", "renewal_period_months", "is_active"
    )
    readonly_fields = ("contract_reference",)
    search_fields = ("partner__name",)
    date_hierarchy = "start_date"


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        "title", "io_reference_number", "contract", "campaign_type", "start_date", "end_date",
        "format", "related_activity", "related_event", "impressions_count", "clicks_count", "conversions_count", 
        "reporting_frequency", "reporting_format", "status", "make_good_status",
    )
    list_filter = ("start_date", "end_date", "contract__partner__name")
    search_fields = ("title","io_reference_number", "contract__partner__name")
    readonly_fields = ("io_reference_number", "impressions_count", "clicks_count", "conversions_count")
    actions = ["activate_ads", "deactivate_ads"]

    def is_active_display(self, obj):
        from django.utils.timezone import now
        return obj.start_date <= now().date() <= obj.end_date
    is_active_display.boolean = True
    is_active_display.short_description = "Actif"

    def activate_ads(self, request, queryset):
        queryset.update(start_date="2024-01-01")
        self.message_user(request, "Pubs activées (attention aux dates réelles)")

    def deactivate_ads(self, request, queryset):
        from datetime import date, timedelta
        queryset.update(end_date=date.today() - timedelta(days=1))
        self.message_user(request, "Pubs désactivées")
    activate_ads.short_description = "Activer les publicités sélectionnées"
    deactivate_ads.short_description = "Désactiver les publicités sélectionnées"

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        # Lien absolu vers ton dashboard
        dashboard_url = reverse('ads:ads_dashboard')
        extra_context['custom_button'] = format_html(
            '<a class="button" style="margin:10px;" href="{}">Aller au Business Dashboard</a>',
            dashboard_url
        )

        return super().changelist_view(request, extra_context=extra_context)


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
    search_fields = ['advertisement__title', 'advertisement__contract__partner__name']
    list_display = ['advertisement', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']


@admin.register(AdInvoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "reference", "advertisement", "period_start", "period_end",
        "generated_at", "total_amount", "tax_amount", "tax_rate", "is_paid"
    )
    readonly_fields = ("reference",)
    list_filter = ("advertisement", "is_paid", "paid_at")
    search_fields = ("advertisement__contract__partner__name", "advertisement__title")
    date_hierarchy = "paid_at"
    actions = ["send_invoice_to_partner"]

    def send_invoice_to_partner(modeladmin, request, queryset):
        success_count = 0
        failure_count = 0
        for invoice in queryset:
            if send_invoice_email(invoice):
                success_count += 1
            else:
                failure_count += 1
        if success_count:
            messages.success(request, f"{success_count} facture(s) envoyée(s) avec succès.")
        if failure_count:
            messages.error(request, f"Erreur lors de l'envoi de {failure_count} facture(s).")


