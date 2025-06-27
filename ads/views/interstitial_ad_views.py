# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/interstitial_ad_views.py
# Author : Morice
# ---------------------------------------------------------------------------

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from math import radians, cos, sin, asin, sqrt

from ads.models import AdImpression, Advertisement,PriorityAd
from ads.serializers import AdvertisementSerializer


def haversine(lat1, lon1, lat2, lon2):
    # Rayon de la Terre en km
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


class InterstitialAdView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        user_lat = request.query_params.get("lat")
        user_lng = request.query_params.get("lng")

        if not user_lat or not user_lng:
            return Response({"error": "Missing lat/lng"}, status=400)

        user_lat = float(user_lat)
        user_lng = float(user_lng)

        priority_ads = (
            PriorityAd.objects
            .filter(
                is_active=True,
                advertisement__format="interstitial",
                advertisement__start_date__lte=now().date(),
                advertisement__end_date__gte=now().date()
            )
            .select_related("advertisement__related_activity", "advertisement__related_event")
        )

        closest_ad = None
        min_dist = float("inf")

        for prio_ad in priority_ads:
            ad = prio_ad.advertisement
            dist = None

            dist_event = None
            if ad.related_event and ad.related_event.latitude and ad.related_event.longitude:
                dist_event = haversine(user_lat, user_lng, ad.related_event.latitude, ad.related_event.longitude)

            dist_activity = None
            if ad.related_activity and ad.related_activity.latitude and ad.related_activity.longitude:
                dist_activity = haversine(user_lat, user_lng, ad.related_activity.latitude, ad.related_activity.longitude)

            # Choisir la distance minimale disponible
            if dist_event is not None and dist_activity is not None:
                dist = min(dist_event, dist_activity)
            elif dist_event is not None:
                dist = dist_event
            elif dist_activity is not None:
                dist = dist_activity
            else:
                continue  # Aucun point géolocalisé, on passe

            if dist < min_dist:
                min_dist = dist
                closest_ad = ad


        if closest_ad:
            AdImpression.objects.create(advertisement=closest_ad, user=user)
            return Response(AdvertisementSerializer(closest_ad).data)

        # Si aucun PriorityAd avec localisation
        return Response({"message": "No interstitial ad available."}, status=204)
