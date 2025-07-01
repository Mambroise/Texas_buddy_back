# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/invoice_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from ads.models import Advertisement, AdInvoice
from ads.services.revenue_calculator import compute_ad_revenue
from decimal import Decimal

class GenerateInvoiceView(APIView):
    def post(self, request, *args, **kwargs):
        partner_id = request.data.get("partner_id")
        start_date = parse_date(request.data.get("start_date"))
        end_date = parse_date(request.data.get("end_date"))

        ads = Advertisement.objects.filter(partner_id=partner_id)

        total_revenue = Decimal("0.00")
        for ad in ads:
            stats = compute_ad_revenue(ad, start_date, end_date)
            total_revenue += stats["revenue"]

        invoice = AdInvoice.objects.create(
            partner_id=partner_id,
            period_start=start_date,
            period_end=end_date,
            total_amount=total_revenue
        )

        return Response({
            "invoice_id": invoice.id,
            "total_amount": float(total_revenue),
            "partner": invoice.partner.name
        })
