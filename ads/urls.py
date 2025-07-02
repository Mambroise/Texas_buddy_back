# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path

from .views.business.admin_logs_export_csv import export_ads_logs_csv
from .views.business.admin_logs_dashboard import ads_logs_dashboard
from .views.ads_tracking_views import TrackClickView, TrackConversionView
from .views.interstitial_ad_views import InterstitialAdView
from .views.push_ad_views import PushNotificationAdView
from django.shortcuts import render
from .views.business.dashboard_views import ads_dashboard
from .views.business.admin_logs_export_pdf import export_ads_logs_pdf

app_name = 'ads'
urlpatterns = [
    path("track-click/", TrackClickView.as_view(), name="track-click"),
    path("track-conversion/", TrackConversionView.as_view(), name="track-conversion"),
    path("interstitial/", InterstitialAdView.as_view(), name="interstitial-ad"), # ok
    path('push/', PushNotificationAdView.as_view(), name='push-ads'), # ok
    path('admin/ads-dashboard/', ads_dashboard, name='ads_dashboard'),
    path('admin/ads-logs-dashboard/', ads_logs_dashboard, name='ads_logs_dashboard'),
    path("admin/ads-logs/export/", export_ads_logs_csv, name="export_ads_logs_csv"),
    path("fr/api/ads/admin/export-logs-pdf/", export_ads_logs_pdf, name="export_ads_logs_pdf"),
    # path("recommend/", GetRecommendedAdView.as_view(), name="recommend-ad"),
]
