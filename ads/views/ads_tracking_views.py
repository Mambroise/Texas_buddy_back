# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/ads_tracking_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from ads.models import Advertisement, AdClick, AdConversion,AdImpression
from core.throttles import PostRateLimitedAPIView
import logging

logger = logging.getLogger(__name__)

class TrackClickView(PostRateLimitedAPIView):
    permission_classes = [AllowAny]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def post(self, request):
        ad_id = request.data.get("ad_id")
        if not ad_id:
            logger.warning("Click tracking failed: missing ad_id.")
            return Response({"error": "Missing ad_id"}, status=400)

        ad = get_object_or_404(Advertisement, pk=ad_id)
        user = request.user if request.user.is_authenticated else None

        AdClick.objects.create(advertisement=ad, user=user)
        ad.clicks_count += 1
        ad.save(update_fields=["clicks_count"])

        logger.info(f"Click tracked for ad {ad.id} (user={user.id if user else 'anonymous'}).")
        return Response({"status": "click recorded", "redirect_url": ad.link_url}, status=200)


class TrackConversionView(PostRateLimitedAPIView):
    permission_classes = [AllowAny]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def post(self, request):
        ad_id = request.data.get("ad_id")
        details = request.data.get("details", {})

        if not ad_id:
            logger.warning("Conversion tracking failed: missing ad_id.")
            return Response({"error": "Missing ad_id"}, status=400)

        ad = get_object_or_404(Advertisement, pk=ad_id)
        user = request.user if request.user.is_authenticated else None

        AdConversion.objects.create(advertisement=ad, user=user, details=details)
        ad.conversions_count += 1
        ad.save(update_fields=["conversions_count"])

        logger.info(f"Conversion tracked for ad {ad.id} (user={user.id if user else 'anonymous'}, details={details}).")
        return Response({"status": "conversion recorded"}, status=201)
    

class TrackImpression():
    # no need for throttles here cause endpoint not exposed. (in app use only)
    @staticmethod
    def track_impression(advertisement, user=None):
        AdImpression.objects.create(advertisement=advertisement, user=user)
        advertisement.impressions_count += 1
        advertisement.save(update_fields=["impressions_count"])

        logger.debug(f"Impression tracked for ad {advertisement.id} (user={user.id if user else 'anonymous'}).")
