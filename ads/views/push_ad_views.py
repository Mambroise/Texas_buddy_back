# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/push_ad_views.py
# Author : Morice
# ---------------------------------------------------------------------------

import logging
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from math import radians, cos, sin, asin, sqrt
from core.throttles import GetRateLimitedAPIView
from ads.models.advertisement import Advertisement

logger = logging.getLogger(__name__)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c

class PushNotificationAdView(GetRateLimitedAPIView):
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        user_lat = request.query_params.get("lat")
        user_lng = request.query_params.get("lng")

        logger.info("[PushAd] Received GET request with lat=%s, lng=%s", user_lat, user_lng)

        if not user_lat or not user_lng:
            logger.warning("[PushAd] Missing latitude or longitude in request.")
            return Response({"error": "Missing lat/lng"}, status=status.HTTP_400_BAD_REQUEST)

        user_lat = float(user_lat)
        user_lng = float(user_lng)

        ads = (
            Advertisement.objects
            .filter(
                format="push",
                start_date__lte=now().date(),
                end_date__gte=now().date()
            )
            .select_related("related_event", "related_activity")
        )
        logger.info("[PushAd] Found %d active push ads", ads.count())

        enriched_ads = []
        skipped_ads = 0

        for ad in ads:
            obj = None
            obj_type = None
            dist = None
            title = None

            if ad.related_event:
                evt = ad.related_event
                if evt.latitude is None or evt.longitude is None:
                    logger.debug("[PushAd] Skipping ad %s: event missing coordinates", ad.id)
                    skipped_ads += 1
                    continue
                dist = haversine(user_lat, user_lng, evt.latitude, evt.longitude)
                if dist > 200:
                    logger.debug("[PushAd] Skipping ad %s: event too far (%.1f km)", ad.id, dist)
                    skipped_ads += 1
                    continue
                obj = evt
                obj_type = "event"
                title = evt.name
                extra_data = {
                    "start_date": evt.start_datetime,
                    "end_date": evt.end_datetime,
                }

            elif ad.related_activity:
                act = ad.related_activity
                if not act.is_unique or act.latitude is None or act.longitude is None:
                    logger.debug("[PushAd] Skipping ad %s: activity not unique or missing coordinates", ad.id)
                    skipped_ads += 1
                    continue
                dist = haversine(user_lat, user_lng, act.latitude, act.longitude)
                if dist > 200:
                    logger.debug("[PushAd] Skipping ad %s: activity too far (%.1f km)", ad.id, dist)
                    skipped_ads += 1
                    continue
                obj = act
                obj_type = "activity"
                title = act.name
                extra_data = {}

            if obj:
                logger.info("[PushAd] Adding ad %s (%.1f km, %s: %s)", ad.id, dist, obj_type, title)
                enriched_ads.append({
                    "ad": ad,
                    "distance": dist,
                    "object_type": obj_type,
                    "object_id": obj.id,
                    "object_title": title,
                    "extra_data": extra_data,
                })

        enriched_ads.sort(key=lambda x: x["distance"])
        logger.info("[PushAd] %d ads enriched and sorted by distance (skipped %d)", len(enriched_ads), skipped_ads)

        response_data = []
        for item in enriched_ads:
            ad_dict = {
                "id": item["ad"].id,
                "format": item["ad"].format,
                "title": item["ad"].title,
                "image_url": item["ad"].image.url if item["ad"].image else None,
                "distance_km": round(item["distance"], 1),
                "object_type": item["object_type"],
                "object_id": item["object_id"],
                "object_title": item["object_title"],
            }
            if item["object_type"] == "event":
                ad_dict["start_date"] = item["extra_data"].get("start_date")
                ad_dict["end_date"] = item["extra_data"].get("end_date")
            response_data.append(ad_dict)

        if not response_data:
            logger.info("[PushAd] No eligible push ads found near user.")
            return Response({"message": "No push ads available."})
