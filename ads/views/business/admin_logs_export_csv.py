# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/admin_logs_export_csv.py
# Author : Morice
# ---------------------------------------------------------------------------


import csv
from itertools import chain
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date

from ads.models import AdImpression, AdClick, AdConversion

def parse_date_safe(date_str):
    if not date_str:
        return None
    parsed = parse_date(date_str)
    if not parsed:
        raise ValueError(f"Format de date invalide: {date_str}")
    return parsed

@staff_member_required
def export_ads_logs_csv(request):
    
    """
    Vue qui exporte les logs filtrés en CSV.
    """
    contract_id = request.GET.get("contract")
    partner_id = request.GET.get("partner")
    advertisement_id = request.GET.get("advertisement")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    log_type = request.GET.get("log_type")  # impression/click/conversion

    # Par défaut : uniquement le 1er jour du mois en cours
    first_day = timezone.now().date().replace(day=1)
    if not start_date:
        start_date = first_day
    else:
        start_date = parse_date_safe(start_date)

    if not end_date:
        end_date = first_day
    else:
        end_date = parse_date_safe(end_date)

    impressions_qs = (
        AdImpression.objects
        .select_related("advertisement", "advertisement__contract", "advertisement__contract__partner")
        .between_dates(start_date, end_date)
    )
    clicks_qs = (
        AdClick.objects
        .select_related("advertisement", "advertisement__contract", "advertisement__contract__partner")
        .between_dates(start_date, end_date)
    )
    conversions_qs = (
        AdConversion.objects
        .select_related("advertisement", "advertisement__contract", "advertisement__contract__partner")
        .between_dates(start_date, end_date)
    )

    if contract_id:
        impressions_qs = impressions_qs.by_contract(contract_id)
        clicks_qs = clicks_qs.by_contract(contract_id)
        conversions_qs = conversions_qs.by_contract(contract_id)

    if partner_id:
        impressions_qs = impressions_qs.by_partner(partner_id)
        clicks_qs = clicks_qs.by_partner(partner_id)
        conversions_qs = conversions_qs.by_partner(partner_id)

    if advertisement_id:
        impressions_qs = impressions_qs.by_advertisement(advertisement_id)
        clicks_qs = clicks_qs.by_advertisement(advertisement_id)
        conversions_qs = conversions_qs.by_advertisement(advertisement_id)

    for obj in impressions_qs:
        obj.log_type = "impression"
    for obj in clicks_qs:
        obj.log_type = "click"
    for obj in conversions_qs:
        obj.log_type = "conversion"

    if log_type == "impression":
        all_logs = impressions_qs
    elif log_type == "click":
        all_logs = clicks_qs
    elif log_type == "conversion":
        all_logs = conversions_qs
    else:
        all_logs = chain(impressions_qs, clicks_qs, conversions_qs)

    all_logs = sorted(all_logs, key=lambda x: x.timestamp, reverse=True)

    # Création du CSV
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="logs_{start_date}_{end_date}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Type",
        "Datetime",
        "IO number",
        "Partner",
        "Contract reference",
        "User id",
        "Details"
    ])

    for log in all_logs:
        writer.writerow([
            log.log_type,
            log.timestamp.strftime("%Y-%m-%d %H:%M"),
            log.advertisement.io_reference_number,
            log.advertisement.contract.partner.legal_name,
            str(log.advertisement.contract),
            log.user.id if log.user else "unknown",
            log.details if log.log_type == "conversion" else ""
        ])

    return response
