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
from .models.priority_ad import PriorityAd
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Q


from .models import Advertisement, Contract
from .services.revenue_calculator import compute_ad_revenue
from .models.ads_types import AdImpression, AdClick, AdConversion



@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "phone", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_email")


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "partner", "campaign_type", "start_date", "duration_months",
        "signed_date","cpm_price", "cpc_price", "cpa_price", "forfait_price", "is_active"
    )
    list_filter = ("campaign_type", "is_active")
    search_fields = ("partner__name",)
    date_hierarchy = "start_date"


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        "title", "contract", "start_date", "end_date",
        "related_activity", "related_event", "is_active_display",
        "impressions_count", "clicks_count", "conversions_count"
    )
    list_filter = ("start_date", "end_date", "contract__partner__name")
    search_fields = ("title", "contract__partner__name")
    readonly_fields = ("impressions_count", "clicks_count", "conversions_count")
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
        "id", "partner", "period_start", "period_end",
        "generated_at", "total_amount", "tax_amount", "tax_rate", "currency", "is_paid"
    )
    list_filter = ("is_paid", "currency", "paid_at")
    search_fields = ("partner__name",)
    date_hierarchy = "paid_at"
    actions = ["mark_as_paid"]

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(is_paid=True, paid_at=datetime.now())
        self.message_user(request, f"{updated} facture(s) marquées comme payées.")


