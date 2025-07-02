# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/admin_logs_export_pdf.py
# Author : Morice
# ---------------------------------------------------------------------------


import os
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from io import BytesIO
from urllib.parse import urlencode
from itertools import chain

from xhtml2pdf import pisa

from ads.models import AdImpression, AdClick, AdConversion
from .admin_logs_dashboard import parse_date_safe


@staff_member_required
def export_ads_logs_pdf(request):
    """
    Exporte un PDF des logs filtrés, en utilisant xhtml2pdf (Pisa).
    """
    # Filtres
    contract_id = request.GET.get("contract")
    partner_id = request.GET.get("partner")
    advertisement_id = request.GET.get("advertisement")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    log_type = request.GET.get("log_type")

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

    # Annoter le type
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

    # Template HTML
    html_string = render_to_string(
        "admin/ads_logs_pdf_template.html",
        {
            "logs": all_logs,
            "start_date": start_date,
            "end_date": end_date,
            "generation_date": timezone.now().strftime("%Y-%m-%d %H:%M"),
            "logo_path": os.path.join(settings.BASE_DIR, "static/images/logo.png")
        }
    )

    # Réponse HTTP
    filename = f"ads_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Génération PDF
    pisa_status = pisa.CreatePDF(html_string, dest=response)

    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF.<pre>" + html_string + "</pre>")

    return response
