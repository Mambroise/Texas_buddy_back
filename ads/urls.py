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
from django.shortcuts import render
from .views.business.dashboard_views import ads_dashboard
from .views.business.generate_invoice_views import generate_invoice
from .views.business.admin_logs_export_pdf import export_ads_logs_pdf
from .views.business.admin_logs_export_xlsx import export_ads_logs_xlsx
from .views.business.admin_logs_export_xml import export_ads_logs_xml
from .views.ads_recommendation import AdvertisementsRecommendationView

app_name = 'ads'

urlpatterns = [
    # ads stats
    path("track-click/", TrackClickView.as_view(), name="track-click"),
    path("track-conversion/", TrackConversionView.as_view(), name="track-conversion"),
    
    path("recommend/", AdvertisementsRecommendationView.as_view(), name="recommend-ad"),
    # Business
    path("generate-invoice/<int:advertisement_id>/", generate_invoice, name="generate_invoice"),
    path('admin/ads-dashboard/', ads_dashboard, name='ads_dashboard'),
    path('admin/ads-logs-dashboard/', ads_logs_dashboard, name='ads_logs_dashboard'),
    # export mothods
    path("admin/ads-logs/export/", export_ads_logs_csv, name="export_ads_logs_csv"),
    path("admin/export-logs-pdf/", export_ads_logs_pdf, name="export_ads_logs_pdf"),
    path("ads/export-impressions-xlsx/", export_ads_logs_xlsx, name="export_impressions_xlsx"),
    path("ads/export-logs-xml/", export_ads_logs_xml, name="export_ads_logs_xml"),

]
