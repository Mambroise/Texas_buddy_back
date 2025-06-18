# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/activity_views.py
# Author : Morice
# ---------------------------------------------------------------------------

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from core.mixins import RetrieveLogMixin
from ..models.activity import Activity
from ..serializers import ActivityDetailSerializer

# ─── View: ActivityDetailAPIView ────────────────────────────────────────────
class ActivityDetailAPIView(RetrieveLogMixin, generics.RetrieveAPIView):
    queryset = Activity.objects.prefetch_related('category', 'promotions')
    serializer_class = ActivityDetailSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
