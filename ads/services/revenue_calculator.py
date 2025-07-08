# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/revenue_calculator.py
# Author : Morice
# ---------------------------------------------------------------------------


from decimal import Decimal
from ads.models import AdImpression, AdClick, AdConversion

def compute_ad_revenue(advertisement, start_date, end_date):
    """
    Calcule le revenu d'une publicité selon son contrat.
    """
    impressions = AdImpression.objects.filter(
        advertisement=advertisement,
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    ).count()

    clicks = AdClick.objects.filter(
        advertisement=advertisement,
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    ).count()

    conversions = AdConversion.objects.filter(
        advertisement=advertisement,
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    ).count()

    contract = advertisement.contract

    revenue = Decimal("0.00")
    breakdown = {}  # pour garder trace des sous-totaux si besoin

    if not contract:
        return {
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "breakdown": breakdown,
        }

    cpm_subtotal = Decimal("0.00")
    cpc_subtotal = Decimal("0.00")
    cpa_subtotal = Decimal("0.00")

    # Cas combo = additionne tous les sous-totaux qui ont un prix renseigné
    if advertisement.campaign_type == "COMBO":
        if advertisement.cpm_price:
            cpm_subtotal = (Decimal(impressions) / Decimal(1000)) * advertisement.cpm_price
        if advertisement.cpc_price:
            cpc_subtotal = Decimal(clicks) * advertisement.cpc_price
        if advertisement.cpa_price:
            cpa_subtotal = Decimal(conversions) * advertisement.cpa_price

        revenue = cpm_subtotal + cpc_subtotal + cpa_subtotal
        breakdown = {
            "CPM": cpm_subtotal,
            "CPC": cpc_subtotal,
            "CPA": cpa_subtotal,
        }

    elif advertisement.campaign_type == "CPM" and advertisement.cpm_price:
        revenue = (Decimal(impressions) / Decimal(1000)) * advertisement.cpm_price
        breakdown = {"CPM": revenue}

    elif advertisement.campaign_type == "CPC" and advertisement.cpc_price:
        revenue = Decimal(clicks) * advertisement.cpc_price
        breakdown = {"CPC": revenue}

    elif advertisement.campaign_type == "CPA" and advertisement.cpa_price:
        revenue = Decimal(conversions) * advertisement.cpa_price
        breakdown = {"CPA": revenue}

    elif advertisement.campaign_type == "PACKAGE" and advertisement.forfait_price:
        revenue = advertisement.forfait_price
        breakdown = {"PACKAGE": revenue}

    elif advertisement.campaign_type == "PREMIUM":
        revenue = advertisement.premium_price or Decimal("0.00")
        breakdown = {"PREMIUM": revenue}

    return {
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "revenue": revenue,
        "breakdown": breakdown,
        "ctr": (Decimal(clicks) / Decimal(impressions) * 100).quantize(Decimal("0.01")) if impressions > 0 else None,
        "cta": (Decimal(conversions) / Decimal(clicks) * 100).quantize(Decimal("0.01")) if clicks > 0 else None,
    }

