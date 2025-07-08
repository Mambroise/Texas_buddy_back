# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/utils.py
# Author : Morice
# ---------------------------------------------------------------------------

import io
from decimal import Decimal, ROUND_HALF_UP
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa

from ads.services.revenue_calculator import compute_ad_revenue


def build_invoice_lines(ad, stats, contract):
    """
    Construit la liste de lignes (CPM, CPC, CPA, Forfait, Pack)
    en fonction du type de campagne.
    """
    lines = []

    # CPM
    cpm_price = ad.cpm_price or Decimal("0")
    imp = stats["impressions"]
    cpm_total = (Decimal(imp) / Decimal("1000")) * cpm_price

    # CPC
    cpc_price = ad.cpc_price or Decimal("0")
    clk = stats["clicks"]
    cpc_total = Decimal(clk) * cpc_price

    # CPA
    cpa_price = ad.cpa_price or Decimal("0")
    conv = stats["conversions"]
    cpa_total = Decimal(conv) * cpa_price

    # COMBO (Forfait)
    combo_price = Decimal("0")
    combo_total = Decimal("0")

    # PACKAGE
    package_price = ad.package_price or Decimal("0")
    package_total = package_price

    # PREMIUM
    premium_price = ad.premium_price or Decimal("0")
    premium_total = premium_price

    # Ajout conditionnel des lignes
    if ad.campaign_type in ["CPM", "COMBO"]:
        lines.append({
            "label": "CPM",
            "count": imp,
            "unit_price": cpm_price,
            "line_total": cpm_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
        })

    if ad.campaign_type in ["CPC", "COMBO"]:
        lines.append({
            "label": "CPC",
            "count": clk,
            "unit_price": cpc_price,
            "line_total": cpc_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
        })

    if ad.campaign_type in ["CPA", "COMBO"]:
        lines.append({
            "label": "CPA",
            "count": conv,
            "unit_price": cpa_price,
            "line_total": cpa_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
        })

    if ad.campaign_type == "PACKAGE":
        lines.append({
            "label": "Package",
            "count": 1,
            "unit_price": package_price,
            "line_total": package_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
        })

    if ad.campaign_type == "PREMIUM":
        lines.append({
            "label": "Pack Premium",
            "count": 1,
            "unit_price": premium_price,
            "line_total": premium_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
        })

    if ad.campaign_type == "COMBO":
        # COMBO ajoute le forfait ET les performances
        lines.append({
            "label": "Combo",
            "count": 1,
            "unit_price": combo_price,
            "line_total": combo_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
        })

    return lines


def generate_invoice_pdf(invoice, company_info):
    """
    Génère un PDF de facture et retourne un buffer BytesIO prêt à être lu.
    Construit aussi les lignes de facturation pour tous les campaign types.
    """
    # 1) calculer stats et lignes
    ad = invoice.advertisement
    contract = ad.contract
    stats = compute_ad_revenue(ad, invoice.period_start, invoice.period_end)
    line_items = build_invoice_lines(ad, stats, contract)

    # 3) préparer le contexte du template
    pdf_context = {
        'invoice': invoice,
        'company_info': company_info,
        'generation_date': timezone.now(),
        'line_items': line_items,

    }
    html = render_to_string("admin/pdf/ad_invoice_pdf.html", pdf_context)

    # 4) générer le PDF en mémoire
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    if pisa_status.err:
        raise Exception("Error while creating invoice.")
    buffer.seek(0)
    return buffer
