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

    revenue = Decimal("0.00")

    contract = advertisement.contract

    if not contract:
        # Pas de contrat = pas de revenu calculable
        return {
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue
        }

    contract_type = contract.campaign_type

    if contract_type == "CPM" and contract.cpm_price:
        revenue = (Decimal(impressions) / Decimal(1000)) * contract.cpm_price
    elif contract_type == "CPC" and contract.cpc_price:
        revenue = Decimal(clicks) * contract.cpc_price
    elif contract_type == "CPA" and contract.cpa_price:
        revenue = Decimal(conversions) * contract.cpa_price
    elif contract_type == "FORFAIT" and contract.forfait_price:
        revenue = contract.forfait_price
    elif contract_type == "PACK":
        # Exemple: pack = forfait (ou 0 si non renseigné)
        revenue = contract.forfait_price or Decimal("0.00")

    return {
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "revenue": revenue
    }


