# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/revenue_calculator.py
# Author : Morice
# ---------------------------------------------------------------------------

from decimal import Decimal
from ads.models import AdImpression, AdClick, AdConversion
import logging

logger = logging.getLogger(__name__)

def compute_ad_revenue(advertisement, start_date, end_date):
    """
    Calcule le revenu d'une publicité selon son contrat.
    """
    logger.debug(f"[RevenueCalculator] Calculating revenue for Ad ID={advertisement.id} "
                 f"from {start_date} to {end_date}")

    impressions = AdImpression.objects.filter(
        advertisement=advertisement,
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    ).count()
    logger.debug(f"[RevenueCalculator] Impressions count: {impressions}")

    clicks = AdClick.objects.filter(
        advertisement=advertisement,
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    ).count()
    logger.debug(f"[RevenueCalculator] Clicks count: {clicks}")

    conversions = AdConversion.objects.filter(
        advertisement=advertisement,
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    ).count()
    logger.debug(f"[RevenueCalculator] Conversions count: {conversions}")

    contract = advertisement.contract

    revenue = Decimal("0.00")
    breakdown = {}

    if not contract:
        logger.warning(f"[RevenueCalculator] No contract associated with Ad ID={advertisement.id}")
        return {
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "breakdown": breakdown,
            "ctr": None,
            "cta": None,
        }

    cpm_subtotal = Decimal("0.00")
    cpc_subtotal = Decimal("0.00")
    cpa_subtotal = Decimal("0.00")

    if advertisement.campaign_type == "COMBO":
        if advertisement.cpm_price:
            cpm_subtotal = (Decimal(impressions) / Decimal(1000)) * advertisement.cpm_price
            logger.debug(f"[RevenueCalculator] CPM subtotal: {cpm_subtotal}")
        if advertisement.cpc_price:
            cpc_subtotal = Decimal(clicks) * advertisement.cpc_price
            logger.debug(f"[RevenueCalculator] CPC subtotal: {cpc_subtotal}")
        if advertisement.cpa_price:
            cpa_subtotal = Decimal(conversions) * advertisement.cpa_price
            logger.debug(f"[RevenueCalculator] CPA subtotal: {cpa_subtotal}")

        revenue = cpm_subtotal + cpc_subtotal + cpa_subtotal
        breakdown = {
            "CPM": cpm_subtotal,
            "CPC": cpc_subtotal,
            "CPA": cpa_subtotal,
        }

    elif advertisement.campaign_type == "CPM" and advertisement.cpm_price:
        revenue = (Decimal(impressions) / Decimal(1000)) * advertisement.cpm_price
        breakdown = {"CPM": revenue}
        logger.debug(f"[RevenueCalculator] CPM revenue: {revenue}")

    elif advertisement.campaign_type == "CPC" and advertisement.cpc_price:
        revenue = Decimal(clicks) * advertisement.cpc_price
        breakdown = {"CPC": revenue}
        logger.debug(f"[RevenueCalculator] CPC revenue: {revenue}")

    elif advertisement.campaign_type == "CPA" and advertisement.cpa_price:
        revenue = Decimal(conversions) * advertisement.cpa_price
        breakdown = {"CPA": revenue}
        logger.debug(f"[RevenueCalculator] CPA revenue: {revenue}")

    elif advertisement.campaign_type == "PACKAGE" and advertisement.forfait_price:
        revenue = advertisement.forfait_price
        breakdown = {"PACKAGE": revenue}
        logger.debug(f"[RevenueCalculator] PACKAGE revenue: {revenue}")

    elif advertisement.campaign_type == "PREMIUM":
        revenue = advertisement.premium_price or Decimal("0.00")
        breakdown = {"PREMIUM": revenue}
        logger.debug(f"[RevenueCalculator] PREMIUM revenue: {revenue}")

    ctr = (Decimal(clicks) / Decimal(impressions) * 100).quantize(Decimal("0.01")) if impressions > 0 else None
    cta = (Decimal(conversions) / Decimal(clicks) * 100).quantize(Decimal("0.01")) if clicks > 0 else None
    logger.debug(f"[RevenueCalculator] CTR: {ctr} %, CTA: {cta} %")

    return {
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "revenue": revenue,
        "breakdown": breakdown,
        "ctr": ctr,
        "cta": cta,
    }
