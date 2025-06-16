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

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
