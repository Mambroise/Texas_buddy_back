# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/revenue_calculator.py
# Author : Morice
# ---------------------------------------------------------------------------

# ads/services/revenue_calculator.py

from decimal import Decimal
from django.db.models import Count
from ads.models import Advertisement, AdImpression, AdClick, AdConversion

def compute_ad_revenue(advertisement, start_date, end_date):
    """
    Calcule le revenu d'une publicité selon son modèle de contrat.
    """
    # Filtrer les logs
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

    contract_type = advertisement.partner.contract_type

    if contract_type == "CPM" and advertisement.cpm_price:
        # CPM = coût pour mille impressions
        revenue = (Decimal(impressions) / Decimal(1000)) * advertisement.cpm_price
    elif contract_type == "CPC" and advertisement.cpc_price:
        revenue = Decimal(clicks) * advertisement.cpc_price
    elif contract_type == "CPA" and advertisement.cpa_price:
        revenue = Decimal(conversions) * advertisement.cpa_price
    elif contract_type == "FORFAIT" and advertisement.forfait_price:
        # Forfait = prix fixe sur la période
        revenue = advertisement.forfait_price
    elif contract_type == "PACK":
        # Ex. tarif pack premium (imaginons que tu définisses un prix pack)
        revenue = advertisement.forfait_price or Decimal("0.00")
    
    return {
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "revenue": revenue
    }
