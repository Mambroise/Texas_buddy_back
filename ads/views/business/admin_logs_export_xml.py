# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/admin_logs_export_xml.py
# Author : Morice
# ---------------------------------------------------------------------------


import xml.etree.ElementTree as ET
from xml.dom import minidom
from itertools import chain
import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date

from ads.models import AdImpression, AdClick, AdConversion

logger = logging.getLogger(__name__)

def parse_date_safe(date_str):
    if not date_str:
        return None
    parsed = parse_date(date_str)
    if not parsed:
        raise ValueError(f"Invalid date format: {date_str}")
    return parsed


@staff_member_required
def export_ads_logs_xml(request):
    """
    Export XML des logs publicitaires avec résumé KPI
    """
    contract_id = request.GET.get("contract")
    partner_id = request.GET.get("partner")
    advertisement_id = request.GET.get("advertisement")
    start_date = parse_date_safe(request.GET.get("start_date")) or timezone.now().date().replace(day=1)
    end_date = parse_date_safe(request.GET.get("end_date")) or timezone.now().date()

    # Querysets filtrés
    impressions = AdImpression.objects.select_related("advertisement", "advertisement__contract", "advertisement__contract__partner").between_dates(start_date, end_date)
    clicks = AdClick.objects.select_related("advertisement", "advertisement__contract", "advertisement__contract__partner").between_dates(start_date, end_date)
    conversions = AdConversion.objects.select_related("advertisement", "advertisement__contract", "advertisement__contract__partner").between_dates(start_date, end_date)

    if contract_id:
        impressions = impressions.by_contract(contract_id)
        clicks = clicks.by_contract(contract_id)
        conversions = conversions.by_contract(contract_id)

    if partner_id:
        impressions = impressions.by_partner(partner_id)
        clicks = clicks.by_partner(partner_id)
        conversions = conversions.by_partner(partner_id)

    if advertisement_id:
        impressions = impressions.by_advertisement(advertisement_id)
        clicks = clicks.by_advertisement(advertisement_id)
        conversions = conversions.by_advertisement(advertisement_id)

    ads = {ad.id: ad for ad in set(i.advertisement for i in chain(impressions, clicks, conversions))}

    # Racine
    root = ET.Element("AdsLogsExport", {
        "start_date": str(start_date),
        "end_date": str(end_date)
    })

    # Résumé KPI
    summary = ET.SubElement(root, "Summary")
    for ad_id, ad in ads.items():
        count_impr = impressions.filter(advertisement_id=ad_id).count()
        count_click = clicks.filter(advertisement_id=ad_id).count()
        count_conv = conversions.filter(advertisement_id=ad_id).count()
        ctr = round((count_click / count_impr) * 100, 2) if count_impr else 0
        conv_rate = round((count_conv / count_click) * 100, 2) if count_click else 0

        ad_el = ET.SubElement(summary, "Ad", {
            "io_number": ad.io_reference_number,
            "partner": ad.contract.partner.legal_name,
            "contract": str(ad.contract),
            "impressions": str(count_impr),
            "clicks": str(count_click),
            "conversions": str(count_conv),
            "ctr_percent": str(ctr),
            "conversion_rate_percent": str(conv_rate)
        })

    # Détail logs
    def create_log_section(name, queryset, include_details=False):
        section = ET.SubElement(root, name)
        for log in queryset.order_by("timestamp"):
            entry = ET.SubElement(section, "Log")
            ET.SubElement(entry, "Timestamp").text = log.timestamp.strftime("%Y-%m-%d %H:%M")
            ET.SubElement(entry, "IONumber").text = log.advertisement.io_reference_number
            ET.SubElement(entry, "Partner").text = log.advertisement.contract.partner.legal_name
            ET.SubElement(entry, "Contract").text = str(log.advertisement.contract)
            ET.SubElement(entry, "UserID").text = str(log.user.id if log.user else "unknown")
            if include_details:
                ET.SubElement(entry, "Details").text = str(log.details or "")

    create_log_section("Impressions", impressions)
    create_log_section("Clicks", clicks)
    create_log_section("Conversions", conversions, include_details=True)

    # Génération propre avec indentation
    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    # Réponse HTTP
    response = HttpResponse(pretty_xml, content_type="application/xml")
    response["Content-Disposition"] = f'attachment; filename="logs_publicitaires_{start_date}_{end_date}.xml"'

    logger.info(
        "[PXMLDF EXPORT] logs made by %s | start_date=%s | end_date=%s | contract_id=%s | partner_id=%s | advertisement_id=%s | impressions=%d | clicks=%d | conversions=%d",
        request.user.email,
        start_date,
        end_date,
        contract_id,
        partner_id,
        advertisement_id,
        impressions.count(),
        clicks.count(),
        conversions.count(),
    )

    return response
