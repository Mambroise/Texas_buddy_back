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
    avec count, unit_price et line_total arrondi à 2 décimales.
    """
    lines = []

    # CPM
    cpm_price = contract.cpm_price or Decimal("0")
    imp = stats["impressions"]
    cpm_total = (Decimal(imp) / Decimal("1000")) * cpm_price
    lines.append({
        "label": "CPM",
        "count": imp,
        "unit_price": cpm_price,
        "line_total": cpm_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
    })

    # CPC
    cpc_price = contract.cpc_price or Decimal("0")
    clk = stats["clicks"]
    cpc_total = Decimal(clk) * cpc_price
    lines.append({
        "label": "CPC",
        "count": clk,
        "unit_price": cpc_price,
        "line_total": cpc_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
    })

    # CPA
    cpa_price = contract.cpa_price or Decimal("0")
    conv = stats["conversions"]
    cpa_total = Decimal(conv) * cpa_price
    lines.append({
        "label": "CPA",
        "count": conv,
        "unit_price": cpa_price,
        "line_total": cpa_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
    })

    # Forfait
    forfait_price = contract.forfait_price or Decimal("0")
    forfait_count = 1 if forfait_price > 0 else 0
    forfait_total = forfait_price * forfait_count
    lines.append({
        "label": "Forfait",
        "count": forfait_count,
        "unit_price": forfait_price,
        "line_total": forfait_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
    })

    # Pack Premium
    pack_price = contract.forfait_price or Decimal("0")
    pack_count = 1 if contract.campaign_type == "PACK" else 0
    pack_total = pack_price * pack_count
    lines.append({
        "label": "Pack Premium",
        "count": pack_count,
        "unit_price": pack_price,
        "line_total": pack_total.quantize(Decimal("0.01"), ROUND_HALF_UP)
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

    # 2) totaliser
    total_amount = sum(item["line_total"] for item in line_items)
    total_amount = Decimal(total_amount).quantize(Decimal("0.01"), ROUND_HALF_UP)

    # 3) préparer le contexte du template
    pdf_context = {
        'invoice': invoice,
        'company_info': company_info,
        'generation_date': timezone.now(),
        'line_items': line_items,
        'total_amount': total_amount,
    }
    html = render_to_string("admin/pdf/ad_invoice_pdf.html", pdf_context)

    # 4) générer le PDF en mémoire
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    if pisa_status.err:
        raise Exception("Erreur lors de la génération du PDF de facture.")
    buffer.seek(0)
    return buffer
