# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/generate_invoice_views.py
# Author : Morice
# ---------------------------------------------------------------------------


import dateparser
from dateutil.relativedelta import relativedelta
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

    # Validation des dates de facturation
    contract = ad.contract

    # 1. Vérifie si la période demandée est hors de la plage de la campagne
    if start_date < ad.start_date:
        messages.error(request, f"La date de début de facturation ({start_date}) est antérieure au début de la campagne ({ad.start_date}).")
        return redirect("ads:ads_dashboard")

    if end_date > ad.end_date:
        messages.error(request, f"La date de fin de facturation ({end_date}) est postérieure à la fin de la campagne ({ad.end_date}).")
        return redirect("ads:ads_dashboard")

    # 2. Vérifie si la période est aussi cohérente avec la période du contrat
    contract_end_date = contract.start_date + relativedelta(months=contract.duration_months)

    if start_date < contract.start_date:
        messages.error(request, f"La date de début de facturation ({start_date}) est antérieure à la date de début du contrat ({contract.start_date}).")
        return redirect("ads:ads_dashboard")

    if end_date > contract_end_date:
        messages.error(request, f"La date de fin de facturation ({end_date}) dépasse la durée du contrat (fin prévue : {contract_end_date}).")
        return redirect("ads:ads_dashboard")


    stats = compute_ad_revenue(ad, start_date, end_date)

    total_excl = stats["revenue"]
    if not isinstance(total_excl, Decimal):
        total_excl = Decimal(total_excl)

    total_excl = total_excl.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # On récupère le taux de taxe de l'annonce (ou du contrat si tu préfères)
    tax_rate = ad.tax_rate or Decimal("0.00")

    if tax_rate > 0:
        tax_amount = (total_excl * tax_rate / Decimal("100")).quantize(Decimal('0.01'))
        total_incl = (total_excl + tax_amount).quantize(Decimal('0.01'))
    else:
        tax_amount = Decimal("0.00")
        total_incl = total_excl

    existing_invoice = AdInvoice.objects.filter(
        advertisement=ad,
        period_start=start_date,
        period_end=end_date
    ).first()

    if existing_invoice:
        messages.warning(request, f"Invoice already exists for this period ({existing_invoice.reference}).")
        return redirect("ads:ads_dashboard")

    invoice = AdInvoice.objects.create(
        advertisement=ad,
        period_start=start_date,
        period_end=end_date,
        period_impressions_count=stats["impressions"],
        period_clicks_count=stats["clicks"],
        period_conversions_count=stats["conversions"],
        total_excluding_tax=total_excl,
        tax_amount=tax_amount,
        total_amount=total_incl,
        tax_rate=tax_rate,
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
