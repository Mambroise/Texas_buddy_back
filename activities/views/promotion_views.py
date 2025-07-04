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

from ..models.promotion import Promotion
from ..serializers import PromotionSerializer
from core.mixins import ListLogMixin

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
