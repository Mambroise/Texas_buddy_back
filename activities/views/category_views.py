# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/views/category_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models.category import Category
from ..serializers import CategorySerializer
from core.mixins import ListLogMixin

# ─── View: CategoryListAPIView ──────────────────────────────────────────────
# no rate limiting here, as categories are static and don't change often
class CategoryListAPIView(ListLogMixin,generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
