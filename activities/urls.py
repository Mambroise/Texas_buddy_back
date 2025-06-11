# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from .views.activity_views import ActivityListAPIView,ActivityDetailAPIView
from .views.event_views import EventListAPIView,EventDetailAPIView

app_name = 'activities'
urlpatterns = [
    path("activities/", ActivityListAPIView.as_view(), name="activity-list"),
    path('activities/<int:id>/', ActivityDetailAPIView.as_view(), name='activity-detail'),
    path("events/", EventListAPIView.as_view(), name="event-list"),
    path("events/<int:id>/", EventDetailAPIView.as_view(), name="event-detail"),
 ]
