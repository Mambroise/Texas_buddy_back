# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/activity_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from ..models.activity import Activity
from ..serializers import ActivitySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..filters import ActivityFilter

class ActivityListAPIView(generics.ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ActivityFilter
    search_fields = ['name', 'description', 'city', 'state']
    ordering_fields = ['rating', 'price_range', 'name']
    ordering = ['name']
    permission_classes = [IsAuthenticated] 



class ActivityDetailAPIView(generics.RetrieveAPIView):
    queryset = Activity.objects.select_related('category').prefetch_related('discounts')
    serializer_class = ActivitySerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]  # Auth obligatoire

