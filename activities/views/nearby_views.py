# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/nearby_views.py
# Author : Morice
# ---------------------------------------------------------------------------

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Func, FloatField, Q
from django.utils import timezone
from datetime import datetime
from core.throttles import GetRateLimitedAPIView

from activities.models import Activity, Event
from activities.serializers import ActivityListSerializer, EventSerializer
from ads.models import Advertisement
from ads.views.ads_tracking_views import TrackImpression
from ads.services.ad_scoring import AdScoringService

# ─── Logger Setup ──────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


from math import radians, cos, sin, acos

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Rayon de la terre en km
    try:
        return round(R * acos(
            cos(radians(lat1)) * cos(radians(lat2)) *
            cos(radians(lon2) - radians(lon1)) +
            sin(radians(lat1)) * sin(radians(lat2))
        ), 3)
    except ValueError:
        # acos peut parfois dépasser légèrement [-1,1] à cause des arrondis
        return None


class NearbyPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ─── View: NearbyListAPIView ────────────────────────────────────────────────
# Return nearby activities and/or events for a given position
class NearbyListAPIView(GetRateLimitedAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [] # Disable throttling for this view, as it's already rate-limited by the base class

    def get(self, request, *args, **kwargs):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        if not (lat and lng):
            logger.error("[NEARBY_SEARCH] Missing lat/lng parameters in request: %s", request.query_params)
            return Response({"error": "Missing 'lat' and 'lng' query parameters."}, status=400)

        try:
            user_lat = float(lat)
            user_lng = float(lng)
        except ValueError:
            logger.error("[NEARBY_SEARCH] Invalid lat/lng format: lat=%s lng=%s", lat, lng)
            return Response({"error": "Invalid latitude or longitude."}, status=400)

        date_str = request.query_params.get('date')
        try:
            reference_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()
        except ValueError:
            logger.warning("[NEARBY_SEARCH] Invalid date format '%s', using today", date_str)
            reference_date = timezone.now().date()

        type_filter = request.query_params.get('type')  # 'activity', 'event', or None
        category_param = request.query_params.get('category')
        search_param = request.query_params.get('search')
        ordering_param = request.query_params.get('ordering')

        logger.info(
            "[NEARBY_SEARCH] lat=%s lng=%s date=%s type=%s category=%s search=%s ordering=%s",
            user_lat, user_lng, reference_date, type_filter, category_param, search_param, ordering_param
        )

        # Define Haversine formula as a custom annotation
        class Haversine(Func):
            function = ''
            template = """
            (6371 * acos(
                cos(radians(%(lat)s)) * cos(radians(latitude)) *
                cos(radians(longitude) - radians(%(lng)s)) +
                sin(radians(%(lat)s)) * sin(radians(latitude))
            ))
            """ % {'lat': user_lat, 'lng': user_lng}
            output_field = FloatField()

        def build_queryset(base_queryset, is_event=False):
            qs = base_queryset.prefetch_related("category", "promotions")

            if is_event:
                qs = qs.filter(
                    is_public=True,
                    start_datetime__date__lte=reference_date,
                    end_datetime__date__gte=reference_date
                )

            if category_param:
                qs = qs.filter(category__name__icontains=category_param)

            if search_param:
                qs = qs.filter(
                    Q(name__icontains=search_param) | Q(description__icontains=search_param)
                )

            qs = qs.annotate(distance=Haversine())

            allowed_ordering = ['price', '-price', 'name', '-name', 'distance', '-distance']

            if ordering_param in allowed_ordering:
                qs = qs.order_by(ordering_param)
            else:
                qs = qs.order_by('distance')

            return qs

        # ─── Load active advertisements ─────────────────────────────────────────
        # today = timezone.now().date()
        # ads_qs = Advertisement.objects.filter(
        #     format="native",
        #     start_date__lte=today,
        #     end_date__gte=today
        # ).order_by("?")[:2]  # Random order or apply your own ordering

        # Service de scoring
        user = request.user
        ad_format="native"
        ad_service = AdScoringService(user, ad_format, user_lat, user_lng)
        ads_qs = ad_service.get_best_ads()

        serialized_ads = []
        for ad in ads_qs:
            ad_item = None
            if ad.related_activity:
                ad_item = ad.related_activity
                serializer = ActivityListSerializer(ad_item, context={'request': request})
                data = serializer.data
                data["type"] = "activity"

                # Calcul distance pour l'activité
                if ad_item.latitude is not None and ad_item.longitude is not None:
                    dist = haversine_distance(user_lat, user_lng, ad_item.latitude, ad_item.longitude)
                    data["distance"] = dist if dist is not None else 999999
                else:
                    data["distance"] = 999999

            elif ad.related_event:
                ad_item = ad.related_event
                serializer = EventSerializer(ad_item, context={'request': request})
                data = serializer.data
                data["type"] = "event"

                # Calcul distance pour l'événement
                if ad_item.latitude is not None and ad_item.longitude is not None:
                    dist = haversine_distance(user_lat, user_lng, ad_item.latitude, ad_item.longitude)
                    data["distance"] = dist if dist is not None else 999999
                else:
                    data["distance"] = 999999
            else:
                continue

            data["is_advertisement"] = True
            serialized_ads.append(data)

            # BUSINESS LOGIC: Track ad impressions
            # Track ad impression if user is authenticated
            if ad:
                TrackImpression().track_impression(advertisement=ad, user=request.user)
                

        logger.info("[NEARBY_SEARCH] %d active advertisements prepared", len(serialized_ads))

        # ─── Load nearby activities and events ──────────────────────────────────
        activity_serialized = []
        event_serialized = []

        if type_filter in [None, '', 'activity']:
            activity_qs = build_queryset(Activity.objects.all())
            activity_serialized = ActivityListSerializer(
                activity_qs,
                many=True,
                context={'request': request}
            ).data

            for item in activity_serialized:
                item['type'] = 'activity'

            logger.info("[NEARBY_SEARCH] %d nearby activities found", len(activity_serialized))

        if type_filter in [None, '', 'event']:
            event_qs = build_queryset(Event.objects.all(), is_event=True)
            event_serialized = EventSerializer(
                event_qs,
                many=True,
                context={'request': request}
            ).data

            for item in event_serialized:
                item['type'] = 'event'

            logger.info("[NEARBY_SEARCH] %d nearby events found", len(event_serialized))

        # ─── Combine ads + standard results ─────────────────────────────────────
        combined = []
        combined.extend(serialized_ads)  # Ads always first
        combined.extend(activity_serialized)
        combined.extend(event_serialized)

        # Sort by distance if available (ads may not have distance)
        combined.sort(key=lambda x: x.get('distance', 999999))

        paginator = NearbyPagination()
        page = paginator.paginate_queryset(combined, request)

        logger.info("[NEARBY_SEARCH] Returning %d items in paginated response", len(page) if page else 0)

        return paginator.get_paginated_response(page)
