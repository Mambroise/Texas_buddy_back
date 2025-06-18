# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from .views.activity_views import ActivityDetailAPIView
from .views.event_views import EventDetailAPIView
from .views.category_views import CategoryListAPIView
from .views.nearby_views import NearbyListAPIView
from .views.all_events_views import CurrentYearEventsList
from .views.promotion_views import PromotionListAPIView

app_name = 'activities'
urlpatterns = [
    path("nearby/", NearbyListAPIView.as_view(), name="nearby-list"), # all activities and events nearby the user or the location in tripDay
    path("activities/<int:id>/", ActivityDetailAPIView.as_view(), name='activity-detail'), # activity all details
    path('events/current_year/', CurrentYearEventsList.as_view(), name='events-current-year'), # all events happening currently the whole year
    path("events/<int:id>/", EventDetailAPIView.as_view(), name="event-detail"), # event all details
    path("categories/", CategoryListAPIView.as_view(), name="category-list"),
    path("promotions/", PromotionListAPIView.as_view(), name="category-list"),
 ]

