# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/dashboard_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from ads.models import Advertisement
from ads.services.revenue_calculator import compute_ad_revenue

class AdsDashboardView(APIView):
    def get(self, request, *args, **kwargs):
        # Paramètres période
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required."}, status=400)
        
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        ads = Advertisement.objects.select_related("partner").all()

        dashboard_data = []

        for ad in ads:
            stats = compute_ad_revenue(ad, start_date, end_date)
            dashboard_data.append({
                "ad_id": ad.id,
                "title": ad.title,
                "partner": ad.partner.name,
                "format": ad.format,
                "impressions": stats["impressions"],
                "clicks": stats["clicks"],
                "conversions": stats["conversions"],
                "revenue": float(stats["revenue"]),
            })

        return Response(dashboard_data)
