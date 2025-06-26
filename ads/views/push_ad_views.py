# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/push_ad_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from math import radians, cos, sin, asin, sqrt

from ads.models.advertisement import Advertisement

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c

class PushNotificationAdView(APIView):

    def get(self, request, *args, **kwargs):
        user_lat = request.query_params.get("lat")
        user_lng = request.query_params.get("lng")

        if not user_lat or not user_lng:
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

        enriched_ads = []

        for ad in ads:
            obj = None
            obj_type = None
            dist = None
            title = None

            if ad.related_event:
                evt = ad.related_event
                if evt.is_national or evt.is_unique or evt.latitude is None or evt.longitude is None:
                    continue
                dist = haversine(user_lat, user_lng, evt.latitude, evt.longitude)
                if dist > 100:
                    continue
                obj = evt
                obj_type = "event"
                title = evt.title
            elif ad.related_activity:
                act = ad.related_activity
                if act.latitude is None or act.longitude is None:
                    continue
                dist = haversine(user_lat, user_lng, act.latitude, act.longitude)
                if dist > 100:
                    continue
                obj = act
                obj_type = "activity"
                title = act.name

            if obj:
                enriched_ads.append({
                    "ad": ad,
                    "distance": dist,
                    "object_type": obj_type,
                    "object_id": obj.id,
                    "object_title": title
                })

        # Tri par distance croissante
        enriched_ads.sort(key=lambda x: x["distance"])

        # Transformation en JSON final
        response_data = []
        for item in enriched_ads:
            response_data.append({
                "id": item["ad"].id,
                "format": item["ad"].format,
                "title": item["ad"].title,
                "image_url": item["ad"].image_url,
                "distance_km": round(item["distance"], 1),
                "object_type": item["object_type"],
                "object_id": item["object_id"],
                "object_title": item["object_title"],
            })

        if not response_data:
            return Response({"message": "No push ads available."}, status=204)

        return Response(response_data, status=200)
