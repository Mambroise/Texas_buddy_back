# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/interstitial_ad_views.py
# Author : Morice
# ---------------------------------------------------------------------------

import logging
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from math import radians, cos, sin, asin, sqrt
from django.db.models import Q
from core.throttles import GetRateLimitedAPIView

from ads.models import PriorityAd
from ads.serializers import AdvertisementSerializer
from ads.views.ads_tracking_views import TrackImpression

logger = logging.getLogger(__name__)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


class InterstitialAdView(GetRateLimitedAPIView):
    throttle_classes = []  # Already rate-limited by the base class

    def get(self, request, *args, **kwargs):
        logger.info("Received interstitial ad request.")

        user = request.user if request.user.is_authenticated else None
        user_lat = request.query_params.get("lat")
        user_lng = request.query_params.get("lng")

        if not user_lat or not user_lng:
            logger.warning("Missing lat/lng parameters in request.")
            return Response({"error": "Missing lat/lng"}, status=400)

        user_lat = float(user_lat)
        user_lng = float(user_lng)
        logger.debug(f"User coordinates received: lat={user_lat}, lng={user_lng}")

        priority_ads = (
            PriorityAd.objects
            .filter(
                Q(advertisement__format="interstitial") |
                Q(advertisement__format="video_interstitial"),
                is_active=True,
                advertisement__start_date__lte=now().date(),
                advertisement__end_date__gte=now().date()
            )
            .select_related("advertisement__related_activity", "advertisement__related_event")
        )

        logger.debug(f"{priority_ads.count()} active priority interstitial ads found.")

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

            if dist_event is not None and dist_activity is not None:
                dist = min(dist_event, dist_activity)
            elif dist_event is not None:
                dist = dist_event
            elif dist_activity is not None:
                dist = dist_activity
            else:
                continue  # No geo info, skip

            logger.debug(f"Ad ID {ad.id}: closest distance calculated = {dist:.2f} km")

            if dist < min_dist:
                min_dist = dist
                closest_ad = ad

        if closest_ad:
            logger.info(f"Closest interstitial ad selected: ID {closest_ad.id} (distance: {min_dist:.2f} km)")
            TrackImpression().track_impression(advertisement=closest_ad, user=user)
            logger.debug(f"Ad impression recorded for ad ID {closest_ad.id}")
            return Response(AdvertisementSerializer(closest_ad).data)

        logger.info("No suitable interstitial ad found for current location.")
        return Response({"message": "No interstitial ad available."}, status=204)
