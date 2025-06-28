# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from .views.ads_tracking_views import TrackClickView, TrackConversionView
from .views.interstitial_ad_views import InterstitialAdView
from .views.push_ad_views import PushNotificationAdView
# from .views.ads_recommendation import GetRecommendedAdView

app_name = 'ads'
urlpatterns = [
    path("track-click/", TrackClickView.as_view(), name="track-click"),
    path("track-conversion/", TrackConversionView.as_view(), name="track-conversion"),
    path("interstitial/", InterstitialAdView.as_view(), name="interstitial-ad"), # ok
    path('push/', PushNotificationAdView.as_view(), name='push-ads'), # ok
    # path("recommend/", GetRecommendedAdView.as_view(), name="recommend-ad"),
]
