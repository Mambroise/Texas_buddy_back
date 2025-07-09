# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/generate_invoice_views.py
# Author : Morice
# ---------------------------------------------------------------------------

import logging
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

logger = logging.getLogger(__name__)

@staff_member_required
def generate_invoice(request, advertisement_id):
    user = request.user
    logger.info(f"[GENERATE_INVOICE] Requested by {user} ({user.email}) for Advertisement ID {advertisement_id}")

    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    start_date = parse_date_safe(start_date_str)
    end_date = parse_date_safe(end_date_str)

    logger.info(f"[GENERATE_INVOICE] Invoice period - Start: {start_date}, End: {end_date}")

    if not start_date or not end_date:
        logger.warning("[GENERATE_INVOICE] Missing start or end date.")
        messages.error(request, "Please provide both start and end dates for the invoice period.")
        return redirect("ads:ads_dashboard")

    ad = get_object_or_404(
        Advertisement.objects.select_related("contract"),
        id=advertisement_id
    )

    contract = ad.contract

    # --- Validation checks ---
    if start_date < ad.start_date:
        logger.warning(f"[GENERATE_INVOICE] Start date {start_date} is before campaign start {ad.start_date}")
        messages.error(request, f"The invoice start date ({start_date}) is before the campaign start ({ad.start_date}).")
        return redirect("ads:ads_dashboard")

    if end_date > ad.end_date:
        logger.warning(f"[GENERATE_INVOICE] End date {end_date} is after campaign end {ad.end_date}")
        messages.error(request, f"The invoice end date ({end_date}) is after the campaign end ({ad.end_date}).")
        return redirect("ads:ads_dashboard")

    contract_end_date = contract.start_date + relativedelta(months=contract.duration_months)

    if start_date < contract.start_date:
        logger.warning(f"[GENERATE_INVOICE] Start date {start_date} is before contract start {contract.start_date}")
        messages.error(request, f"The invoice start date ({start_date}) is before the contract start date ({contract.start_date}).")
        return redirect("ads:ads_dashboard")

    if end_date > contract_end_date:
        logger.warning(f"[GENERATE_INVOICE] End date {end_date} exceeds contract duration (ends: {contract_end_date})")
        messages.error(request, f"The invoice end date ({end_date}) exceeds the contract duration (ends: {contract_end_date}).")
        return redirect("ads:ads_dashboard")

    # --- Revenue computation ---
    stats = compute_ad_revenue(ad, start_date, end_date)
    total_excl = stats["revenue"]
    if not isinstance(total_excl, Decimal):
        total_excl = Decimal(total_excl)

    total_excl = total_excl.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    logger.info(f"[GENERATE_INVOICE] Revenue (excl. tax): {total_excl} USD")

    tax_rate = ad.tax_rate or Decimal("0.00")
    if tax_rate > 0:
        tax_amount = (total_excl * tax_rate / Decimal("100")).quantize(Decimal('0.01'))
        total_incl = (total_excl + tax_amount).quantize(Decimal('0.01'))
    else:
        tax_amount = Decimal("0.00")
        total_incl = total_excl

    logger.info(f"[GENERATE_INVOICE] Tax rate: {tax_rate}%, Tax amount: {tax_amount}, Total incl. tax: {total_incl}")

    # --- Check for duplicate invoice ---
    existing_invoice = AdInvoice.objects.filter(
        advertisement=ad,
        period_start=start_date,
        period_end=end_date
    ).first()

    if existing_invoice:
        logger.warning(f"[GENERATE_INVOICE] Invoice already exists: {existing_invoice.reference}")
        messages.warning(request, f"Invoice already exists for this period ({existing_invoice.reference}).")
        return redirect("ads:ads_dashboard")

    # --- Create new invoice ---
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

    logger.info(f"[GENERATE_INVOICE] Invoice {invoice.reference} created successfully for Ad ID {advertisement_id}")
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
    logger.error(f"[PARSE_DATE_SAFE] Invalid date format: {date_str}")
    raise ValueError(f"Format de date invalide: {date_str}. Essayez 'YYYY-MM-DD' ou '1 juillet 2025'")
