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

from ..models import AdImpression, Advertisement,PriorityAd
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
            return Response({"error": "Missing lat/lng"}, status=status.HTTP_400_BAD_REQUEST)

        user_lat = float(user_lat)
        user_lng = float(user_lng)

        # 1. PriorityAd actif
        priority_ad = (
            PriorityAd.objects
            .filter(is_active=True, advertisement__format="interstitial",
                    advertisement__start_date__lte=now().date(),
                    advertisement__end_date__gte=now().date())
            .select_related("advertisement")
            .first()
        )
        if priority_ad:
            AdImpression.objects.create(advertisement=priority_ad.advertisement, user=user)
            return Response(AdvertisementSerializer(priority_ad.advertisement).data)

        # 2. Event national 
        national_event_ads = (
            Advertisement.objects
            .filter(
                format="interstitial",
                related_event__is_national=True,
                related_event__end_date__gte=now().date(),
                start_date__lte=now().date(),
                end_date__gte=now().date()
            )
            .order_by('related_event__start_date')
        )
        if national_event_ads.exists():
            return Response(AdvertisementSerializer(national_event_ads.first()).data)

        # 3. Activity is_unique
        nearby_ads = (
            Advertisement.objects
            .filter(
                format="interstitial",
                related_activity__latitude__isnull=False,
                related_activity__longitude__isnull=False,
                start_date__lte=now().date(),
                end_date__gte=now().date()
            )
            .select_related("related_activity")
        )

        closest_ad = None
        min_dist = float("inf")

        for ad in nearby_ads:
            act = ad.related_activity
            dist = haversine(user_lat, user_lng, act.latitude, act.longitude)
            if dist < min_dist:
                min_dist = dist
                closest_ad = ad

        if closest_ad:
            AdImpression.objects.create(advertisement=closest_ad, user=user)
            return Response(AdvertisementSerializer(closest_ad).data)

        return Response({"message": "No interstitial ad available."}, status=204)
