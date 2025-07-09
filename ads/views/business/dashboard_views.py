# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/dashboard_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
import logging


from ads.models import Advertisement, Contract,AdInvoice
from ads.services.revenue_calculator import compute_ad_revenue
from django.utils.dateparse import parse_date

logger = logging.getLogger(__name__)

@staff_member_required
def ads_dashboard(request):
    user = request.user
    logger.info(f"[ADS_DASHBOARD] Accessed by {user} ({user.email})")

    contract_id = request.GET.get("contract")
    advertisement_id = request.GET.get("advertisement")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    logger.info(f"[ADS_DASHBOARD] Filters received - Contract: {contract_id}, Advertisement: {advertisement_id}, Start date: {start_date}, End date: {end_date}")

    # Dates par défaut
    if not start_date:
        start_date = timezone.now().date().replace(day=1)
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    ads_qs = Advertisement.objects.select_related("contract", "contract__partner")

    if contract_id:
        ads_qs = ads_qs.filter(contract__id=contract_id)
    if advertisement_id:
        ads_qs = ads_qs.filter(id=advertisement_id)

    logger.info(f"[ADS_DASHBOARD] Number of ads after filtering: {ads_qs.count()}")

    dashboard_data = []
    total_revenue = 0

    for ad in ads_qs:
        stats = compute_ad_revenue(ad, start_date, end_date)
        total_revenue += stats["revenue"]

        dashboard_data.append({
            "ad": ad,
            "stats": stats
        })

    logger.info(f"[ADS_DASHBOARD] Revenu total calculé : {total_revenue} USD")

    summary_by_type = {}
    for entry in dashboard_data:
        contract_type = entry["ad"].campaign_type
        revenue = entry["stats"]["revenue"]
        if contract_type not in summary_by_type:
            summary_by_type[contract_type] = Decimal("0.00")
        summary_by_type[contract_type] += revenue

    all_ads = Advertisement.objects.all()
    all_contracts = Contract.objects.select_related("partner").all()

    context = {
        "ads": all_ads,
        "contracts": all_contracts,
        "dashboard_data": dashboard_data,
        "total_revenue": total_revenue,
        "summary_by_type": summary_by_type,
        "start_date": start_date,
        "end_date": end_date,
        "request": request,
    }

    logger.info(f"[ADS_DASHBOARD] Dashboard rendered with {len(dashboard_data)} entries.")
    return render(request, "admin/ads_dashboard.html", context)
