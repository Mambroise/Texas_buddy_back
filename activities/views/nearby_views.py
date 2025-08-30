# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/nearby_views.py
# Author : Morice
# ---------------------------------------------------------------------------

import logging
from datetime import datetime, time
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Func, FloatField, Q
from rest_framework.views import APIView

from activities.models import Activity, Event
from activities.serializers import ActivityListSerializer, EventSerializer
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
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


class NearbyListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        limit_param = request.query_params.get("limit")

        try:
            raw_limit = int(limit_param) if limit_param is not None else None
        except ValueError:
            raw_limit = None
        cap = max(1, min(raw_limit or 100, 300))  # bornes côté serveur

        # Bounds optionnels (viewport)
        north = request.query_params.get("north")
        south = request.query_params.get("south")
        east  = request.query_params.get("east")
        west  = request.query_params.get("west")

        def apply_bounds(qs):
            if all([north, south, east, west]):
                try:
                    N, S, E, W = float(north), float(south), float(east), float(west)
                    qs = qs.filter(
                        latitude__lte=N, latitude__gte=S,
                        longitude__gte=W, longitude__lte=E
                    )
                except ValueError:
                    pass
            return qs

        if not (lat and lng):
            logger.error("[NEARBY_SEARCH] Missing lat/lng. params=%s", request.query_params)
            return Response({"error": "Missing 'lat' and 'lng' query parameters."}, status=400)

        try:
            user_lat = float(lat)
            user_lng = float(lng)
        except ValueError:
            logger.error("[NEARBY_SEARCH] Invalid lat/lng. lat=%s lng=%s", lat, lng)
            return Response({"error": "Invalid latitude or longitude."}, status=400)

        date_str = request.query_params.get('date')
        try:
            reference_date = (
                datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_str else timezone.now().date()
            )
        except ValueError:
            logger.warning("[NEARBY_SEARCH] Invalid date '%s', using today", date_str)
            reference_date = timezone.now().date()

        type_filter   = request.query_params.get('type')        # 'activity' | 'event' | None
        search_param  = request.query_params.get('search')
        ordering_param = request.query_params.get('ordering')

        # Catégories par icône FA (répétées) ou CSV fallback
        category_keys = request.query_params.getlist('category')
        if not category_keys:
            cats_csv = request.query_params.get('categories')
            if cats_csv:
                category_keys = [c.strip() for c in cats_csv.split(',') if c.strip()]

        logger.info(
            "[NEARBY_SEARCH] lat=%s lng=%s date=%s type=%s cats=%s search=%s ordering=%s cap=%s bounds=%s",
            user_lat, user_lng, reference_date, type_filter, category_keys, search_param, ordering_param, cap,
            (north, south, east, west),
        )

        # Annotation distance
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

        allowed_ordering = ['price', '-price', 'name', '-name', 'distance', '-distance']

        def build_queryset(base_queryset, is_event=False):
            qs = (
                base_queryset
                .select_related("primary_category")
                .prefetch_related("category", "promotions")
            )
    
            start_of_day = timezone.make_aware(datetime.combine(reference_date, time.min))
            end_of_day   = timezone.make_aware(datetime.combine(reference_date, time.max))

            if is_event:
                qs = qs.filter(
                    is_public=True,
                    start_datetime__lte=end_of_day,
                    end_datetime__gte=start_of_day,
                )
            
        
            if not is_event:
                qs = qs.filter(is_active=True)

            if category_keys:
                qs = qs.filter(
                    Q(primary_category__icon__in=category_keys) |
                    Q(category__icon__in=category_keys)
                ).distinct()

            if search_param:
                qs = qs.filter(
                    Q(name__icontains=search_param) |
                    Q(description__icontains=search_param)
                )
            
            qs = qs.defer("description", "image")  # moins de pages lues en mémoire


            qs = apply_bounds(qs)
            qs = qs.annotate(distance=Haversine())

            ordering = ordering_param if ordering_param in allowed_ordering else 'distance'
            qs = qs.order_by(ordering)

            # cap côté SQL (évite de sérialiser trop d'objets)
            return qs[:cap]

        # -------- Ads scoring + sérialisation --------
        user = request.user
        ad_service = AdScoringService(user, "native", user_lat, user_lng)
        ads_qs = ad_service.get_best_ads()

        def haversine_distance(lat1, lon1, lat2, lon2):
            from math import radians, cos, sin, acos
            R = 6371
            try:
                return round(R * acos(
                    cos(radians(lat1)) * cos(radians(lat2)) *
                    cos(radians(lon2) - radians(lon1)) +
                    sin(radians(lat1)) * sin(radians(lat2))
                ), 3)
            except ValueError:
                return None

        serialized_ads = []
        for ad in ads_qs:
            if ad.related_activity:
                obj = ad.related_activity
                data = ActivityListSerializer(obj, context={'request': request}).data
                data["type"] = "activity"
            elif ad.related_event:
                obj = ad.related_event
                data = EventSerializer(obj, context={'request': request}).data
                data["type"] = "event"
            else:
                continue

            if obj.latitude is not None and obj.longitude is not None:
                dist = haversine_distance(user_lat, user_lng, obj.latitude, obj.longitude)
                data["distance"] = dist if dist is not None else 999999
            else:
                data["distance"] = 999999

            data["is_advertisement"] = True
            serialized_ads.append(data)

            TrackImpression().track_impression(advertisement=ad, user=request.user)

        logger.info("[NEARBY_SEARCH] %d active advertisements prepared", len(serialized_ads))

        # -------- Nearby data --------
        activity_serialized = []
        event_serialized = []

        if type_filter in [None, '', 'activity']:
            a_qs = build_queryset(Activity.objects.all())
            activity_serialized = ActivityListSerializer(a_qs, many=True, context={'request': request}).data
            for item in activity_serialized:
                item['type'] = 'activity'
            logger.info("[NEARBY_SEARCH] %d nearby activities", len(activity_serialized))

        if type_filter in [None, '', 'event']:
            e_qs = build_queryset(Event.objects.all(), is_event=True)
            event_serialized = EventSerializer(e_qs, many=True, context={'request': request}).data
            for item in event_serialized:
                item['type'] = 'event'
            logger.info("[NEARBY_SEARCH] %d nearby events", len(event_serialized))

        # -------- Fusion: ads d'abord, puis tri distance sur le reste --------
        non_ads = activity_serialized + event_serialized
        non_ads.sort(key=lambda x: x.get('distance', 999999))

        combined = serialized_ads + non_ads

        paginator = NearbyPagination()
        page = paginator.paginate_queryset(combined, request)

        logger.info("[NEARBY_SEARCH] Returning %d items (paginated)", len(page) if page else 0)
        return paginator.get_paginated_response(page)
