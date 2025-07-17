# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/promotion_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from activities.models import Promotion
from activities.serializers import ActivityDetailSerializer, EventSerializer

from ..models.promotion import Promotion
from ..serializers import PromotionSerializer
from core.mixins import ListLogMixin

import logging
logger = logging.getLogger(__name__)

@method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True), name='dispatch')
class PromotionListAPIView(ListLogMixin,generics.ListAPIView):
    queryset = Promotion.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).select_related("activity", "event")
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity', 'event']



class PromotionResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CurrentPromotionsView(APIView):
    """
    Retourne toutes les activités et événements qui ont une promotion en cours.
    """
    permission_classes = [AllowAny]
    pagination_class = PromotionResultsSetPagination

    def get(self, request, *args, **kwargs):
        now = timezone.now().date()  # compare sur la date
        qs = Promotion.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).select_related('activity', 'event')

        activities = []
        events = []

        for promo in qs:
            if promo.activity:
                activities.append({
                    "promotion": {
                        "id": promo.id,
                        "title": promo.title,
                        "description": promo.description,
                        "discount_type": promo.discount_type,
                        "amount": str(promo.amount),
                        "start_date": promo.start_date,
                        "end_date": promo.end_date,
                    },
                    "activity": ActivityDetailSerializer(promo.activity, context={"request": request}).data
                })
            elif promo.event:
                events.append({
                    "promotion": {
                        "id": promo.id,
                        "title": promo.title,
                        "description": promo.description,
                        "discount_type": promo.discount_type,
                        "amount": str(promo.amount),
                        "start_date": promo.start_date,
                        "end_date": promo.end_date,
                    },
                    "event": EventSerializer(promo.event, context={"request": request}).data
                })

        # Combine les deux listes
        data = {
            "activities_with_promo": activities,
            "events_with_promo": events,
            "count": len(activities) + len(events)
        }

        logger.info("[PROMO_LIST] %d promotions actives retournées", len(qs))

        return Response(data, status=200)
