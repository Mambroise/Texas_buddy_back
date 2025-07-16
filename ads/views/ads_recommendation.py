# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/ads_recommendation.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..services.ad_scoring import AdScoringService
from ..serializers import AdvertisementSerializer
from .ads_tracking_views import TrackImpression

import logging

logger = logging.getLogger(__name__)

class AdvertisementsRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logger.info("Received advertisement recommendation request.")

        # Récupération des paramètres
        ad_format = request.query_params.get('fmt')
        user_lat = request.query_params.get('lat')
        user_lon = request.query_params.get('lng')

        if not ad_format:
            logger.warning("Missing ad format.")
            return Response({'error': 'Ad format is required.'}, status=400)

        try:
            lat = float(user_lat) if user_lat is not None else None
            lon = float(user_lon) if user_lon is not None else None
        except ValueError:
            logger.error("Invalid latitude or longitude.")
            return Response({'error': 'Invalid latitude or longitude.'}, status=400)

        user = request.user
        logger.debug(f"Ad recommendation for user={user.id} ({user.email}), format={ad_format}, lat={lat}, lon={lon}")

        # Service de scoring
        ad_service = AdScoringService(user, ad_format, lat, lon)
        best_ads = ad_service.get_best_ads()
        logger.info(f"Selected {len(best_ads)} ads for recommendation.")

        # 🔥 TRACK IMPRESSIONS pour chaque ad retournée
        for ad in best_ads:
            try:
                TrackImpression().track_impression(advertisement=ad, user=user)
                logger.debug(f"Tracked impression for ad_id={ad.id}, user_id={user.id}")
            except Exception as e:
                logger.exception(f"Failed to track impression for ad_id={ad.id}: {e}")

        serializer = AdvertisementSerializer(best_ads, many=True, context={'request': request})
        return Response(serializer.data, status=200)
