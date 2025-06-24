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
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from activities.models import Activity, Event
from activities.serializers import ActivityListSerializer, EventSerializer

# ─── Logger Setup ──────────────────────────────────────────────────────────
logger = logging.getLogger('texasbuddy')

class NearbyPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# ─── View: NearbyListAPIView ────────────────────────────────────────────────
# Return nearby activities and/or events for a given position
@method_decorator(ratelimit(key='ip', rate='20/m', method='GET', block=True), name='dispatch')
class NearbyListAPIView(APIView):
    permission_classes = [IsAuthenticated]

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

        combined = activity_serialized + event_serialized
        combined.sort(key=lambda x: x.get('distance', 999999))

        paginator = NearbyPagination()
        page = paginator.paginate_queryset(combined, request)

        logger.info("[NEARBY_SEARCH] Returning %d items in paginated response", len(page) if page else 0)

        return paginator.get_paginated_response(page)
