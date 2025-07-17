# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :community/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from .views.review_views import ReviewListCreateView, ReviewDetailView


app_name = 'community'

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view(), name='create-review'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
 ]
