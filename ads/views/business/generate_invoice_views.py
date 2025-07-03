# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/generate_invoice_views.py
# Author : Morice
# ---------------------------------------------------------------------------


import dateparser
from django.utils.dateparse import parse_date
from decimal import Decimal,ROUND_HALF_UP
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from datetime import timedelta
from django.contrib import messages

from ads.models import Advertisement, AdInvoice
from ads.services.revenue_calculator import compute_ad_revenue

@staff_member_required
def generate_invoice(request, advertisement_id):

    # View which generates an invoice for a specific advertisement
    # based on the contract and the period specified in the querystring.

    # Récupérer la période depuis la querystring
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    start_date = parse_date_safe(start_date_str)
    end_date = parse_date_safe(end_date_str)

    if not start_date or not end_date:
        messages.error(request, "Please provide both start and end dates for the invoice period.")
        return redirect("ads:ads_dashboard")

    ad = get_object_or_404(
        Advertisement.objects.select_related("contract"),
        id=advertisement_id
    )
    contract = ad.contract

    stats = compute_ad_revenue(ad, start_date, end_date)

    # Calcul du montant selon le type de campagne
    campaign_type = contract.campaign_type
    total = 0



    if campaign_type == "CPM":
        total = (Decimal(stats["impressions"]) / Decimal("1000")) * (contract.cpm_price or Decimal("0"))
    elif campaign_type == "CPC":
        total = Decimal(stats["clicks"]) * (contract.cpc_price or Decimal("0"))
    elif campaign_type == "CPA":
        total = Decimal(stats["conversions"]) * (contract.cpa_price or Decimal("0"))
    elif campaign_type == "FORFAIT":
        total = contract.forfait_price or Decimal("0")
    elif campaign_type == "PACK":
        total = contract.forfait_price or Decimal("0")

    # Conversion en Decimal si besoin (au cas où total est float)
    if not isinstance(total, Decimal):
        total = Decimal(total)

    # Arrondi à 2 décimales
    total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    existing_invoice = AdInvoice.objects.filter(
        advertisement=ad,
        period_start=start_date,
        period_end=end_date
    ).first()

    if existing_invoice:
        messages.warning(request, f"Invoice already exists for this period ({existing_invoice.reference}).")
        return redirect("ads:ads_dashboard")


    # Création de la facture
    invoice = AdInvoice.objects.create(
        advertisement=ad,
        period_start=start_date,
        period_end=end_date,
        period_impressions_count=stats["impressions"],
        period_clicks_count=stats["clicks"],
        period_conversions_count=stats["conversions"],
        total_excluding_tax=total,  # if you have a tax calculation, adjust here
        total_amount=total,
        tax_amount=0,
        tax_rate=0,
        currency="USD",
        due_date=timezone.now().date() + timedelta(days=30)
    )

    messages.success(request, f"Invoice {invoice.reference} has been successfully generated.")
    return redirect("ads:ads_dashboard")




def parse_date_safe(date_str):
    """
    Essaie de parser la date en ISO, en format long FR, ou avec dateparser.
    """
    if not date_str:
        return None

    # D'abord Django utils
    parsed = parse_date(date_str)
    if parsed:
        return parsed

    # Ensuite dateparser qui comprend '1 juillet 2025'
    parsed = dateparser.parse(date_str, languages=["fr", "en"])
    if parsed:
        return parsed.date()

    raise ValueError(f"Format de date invalide: {date_str}. Essayez 'YYYY-MM-DD' ou '1 juillet 2025'")
