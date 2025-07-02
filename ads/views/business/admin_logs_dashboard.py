# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/admin_logs_dashboard.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from itertools import chain
from django.utils.dateparse import parse_date

from ads.models import Advertisement, Contract, AdImpression, AdClick, AdConversion


def parse_date_safe(date_str):
    """
    Parse la date au format YYYY-MM-DD uniquement.
    """
    if not date_str:
        return None

    parsed = parse_date(date_str)
    if not parsed:
        raise ValueError(f"Format de date invalide: {date_str}")
    return parsed


@staff_member_required
def ads_logs_dashboard(request):
    """
    Vue Dashboard unifié des logs publicitaires.
    """
    from urllib.parse import urlencode

    contract_id = request.GET.get("contract")
    partner_id = request.GET.get("partner")
    advertisement_id = request.GET.get("advertisement")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    log_type = request.GET.get("log_type")  # impression / click / conversion

    # Dates par défaut : premier jour du mois courant
    # Date par défaut: uniquement le 1er jour du mois en cours
    first_day = timezone.now().date().replace(day=1)
    if not start_date:
        start_date = first_day
    else:
        start_date = parse_date_safe(start_date)

    if not end_date:
        end_date = first_day
    else:
        end_date = parse_date_safe(end_date)

    # Base QuerySets
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

    # Filtres supplémentaires
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

    # Attribution du type
    for obj in impressions_qs:
        obj.log_type = "impression"
    for obj in clicks_qs:
        obj.log_type = "click"
    for obj in conversions_qs:
        obj.log_type = "conversion"

    # Sélection selon le filtre log_type
    if log_type == "impression":
        all_logs = impressions_qs
    elif log_type == "click":
        all_logs = clicks_qs
    elif log_type == "conversion":
        all_logs = conversions_qs
    else:
        all_logs = chain(impressions_qs, clicks_qs, conversions_qs)

    # Tri par date décroissante
    all_logs = sorted(all_logs, key=lambda x: x.timestamp, reverse=True)

    all_contracts = Contract.objects.select_related("partner").all()
    all_partners = {c.partner for c in all_contracts}
    all_advertisements = Advertisement.objects.all()

    query_string = urlencode(request.GET, doseq=True)

    context = {
        "contracts": all_contracts,
        "partners": all_partners,
        "advertisements": all_advertisements,
        "logs": all_logs,
        "start_date": start_date,
        "end_date": end_date,
        "request": request,
        "log_type": log_type,
        "query_string": query_string,  # <= ajouté ici
    }
    return render(request, "admin/ads_logs_dashboard.html", context)
