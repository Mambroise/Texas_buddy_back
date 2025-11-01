# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : planners/views/transport_views.py
# Author : Morice
# ---------------------------------------------------------------------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from ..services.transport_service import estimate_travel_minutes_meters
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

@method_decorator(ratelimit(key='ip', rate='50/10m', method='POST', block=True), name='dispatch')
class TransportEstimateView(APIView):
    """
    POST /api/transport/estimate/
    body:
      {
        "origin": {"lat": 32.78, "lng": -96.80},
        "destination": {"lat": 32.79, "lng": -96.81},
        "mode": "driving",
        "lang": "fr"
      }
    """
    throttle_classes = [] # no throttle

    def post(self, request):
        try:
            origin = request.data.get("origin") or {}
            dest   = request.data.get("destination") or {}
            mode   = (request.data.get("mode") or "driving").lower()
            lang   = (request.data.get("lang") or "en")[:5]

            if "lat" not in origin or "lng" not in origin or "lat" not in dest or "lng" not in dest:
                return Response({"detail": _("origin/destination missing coords")},
                                status=status.HTTP_400_BAD_REQUEST)

            minutes, meters = estimate_travel_minutes_meters(
                origin={"lat": float(origin["lat"]), "lng": float(origin["lng"])},
                destination={"lat": float(dest["lat"]), "lng": float(dest["lng"])},
                mode=mode,
                lang=lang,
            )
            return Response({
                "mode": mode,
                "duration_minutes": int(minutes),
                "distance_meters": int(meters),
            })
        except Exception as ex:
            return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
