# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from .views.trip_views import (
    TripListCreateView,
    TripView,
)
from .views.tripday_views import (
    TripDayListCreateView,
    TripDayDetailView
)
from .views.address_cache_views import AddressSelectView, AddressSearchTXView
from .views.tripstep_views import (
    TripDaySyncView,
    TripStepListCreateView,
    TripStepMoveView,
    TripStepDeleteView
)

app_name = 'planners'

urlpatterns = [
    path('trips/', TripListCreateView.as_view(), name='trip-list-create'), # ok
    path('trips/<int:id>/', TripView.as_view(), name='trip-detail'), # ok
    # TripDay views
    # Note: This endpoint is for updating address cache, not creating TripDays
    # It will be used by the mobile app to update address cache for a TripDay
    path("address/search-tx/", AddressSearchTXView.as_view(), name="address-search-tx"),
    path("address/select/", AddressSelectView.as_view(), name="address-select"),
    path("trip-days/address/", AddressSelectView.as_view(), name="address-select"),

    # TripDay CRUD operations
    # Note: TripDays are created automatically when a Trip is created
    path('trip-days/', TripDayListCreateView.as_view(), name='tripday-list-create'), # ok create, 
    path('trip-days/<int:pk>/sync/', TripDaySyncView.as_view(), name='tripday-sync'), # ok sync
    path('trip-days/<int:id>/', TripDayDetailView.as_view(), name='tripday-detail'), # ok delete, ok detail
    # TripStep views
    path('trip-steps/', TripStepListCreateView.as_view(), name='tripstep-list-create'), # ok create ok list
    path('trip-steps/<int:pk>/', TripStepDeleteView.as_view(), name='tripstep-delete'), # ok delete
    path('trip-steps/<int:pk>/move/', TripStepMoveView.as_view(), name='tripstep-move'),
]

