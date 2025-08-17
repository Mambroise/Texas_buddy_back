# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : ads/views/ad_scoring.py
# Author : Morice
# ---------------------------------------------------------------------------


import logging
from datetime import datetime
from django.utils import timezone
from math import radians, sin, cos, sqrt, atan2
from ..models import Advertisement

logger = logging.getLogger(__name__)

# --- scoring Const ---
SCORE_POINTS = {
    "INTEREST_MATCH": 4,
    "PROXIMITY_BONUS": 3,
    "CONTEXT_TIME": 2,
    "CONTEXT_SEASON": 2,
}

class AdScoringService:
    def __init__(self, user, format, user_lat=None, user_lon=None):
        self.user = user
        self.format = format
        self.user_lat = user_lat
        self.user_lon = user_lon
        self.now = timezone.now()

        logger.info(
            f"[AdScoringService] Init for user={self.user.id if self.user else 'anon'}, "
            f"format={self.format}, lat={self.user_lat}, lon={self.user_lon}, time={self.now}"
        )

    def get_best_ads(self):
        """
        Sélectionne les meilleures publicités en fonction du format.
        """
        logger.info(f"[AdScoringService] get_best_ads called with format={self.format}")

        if self.format == "proximity":
            logger.debug("[AdScoringService] Format is proximity → retrieving proximity ads")
            ads = self._get_proximity_ads()
            logger.info(f"[AdScoringService] Found {len(ads)} proximity ads within 200km")
            return ads

        ads = self._get_eligible_ads()
        logger.debug(f"[AdScoringService] Retrieved {ads.count()} eligible ads for scoring")

        scored_ads = self._calculate_scores(ads)
        logger.debug(f"[AdScoringService] Scoring completed for {len(scored_ads)} ads")

        scored_ads.sort(key=lambda x: x['score'], reverse=True)
        logger.debug(
            "[AdScoringService] Top scores: " +
            ", ".join(f"ad#{x['ad_object'].id}:{x['score']}" for x in scored_ads[:5])
        )

        ad_count = 1
        if self.format in ['native', 'push']:
            ad_count = 3

        selected = [ad['ad_object'] for ad in scored_ads[:ad_count]]
        logger.info(
            f"[AdScoringService] Selected {len(selected)} ads for format={self.format} => IDs: {[a.id for a in selected]}"
        )
        return selected

    # -------------------------------------------------------------------
    # Cas particulier: proximity
    # -------------------------------------------------------------------
    def _get_proximity_ads(self):
        ads = Advertisement.objects.filter(
            status="ACTIVE",
            format="proximity",
            start_date__lte=self.now.date(),
            end_date__gte=self.now.date()
        ).select_related("related_activity", "related_event")

        logger.debug(f"[AdScoringService] Proximity ads query returned {ads.count()} ads")

        if self.user_lat is None or self.user_lon is None:
            logger.warning("[AdScoringService] User lat/lon missing for proximity filtering")
            return []

        eligible_ads = []
        for ad in ads:
            latlon = self._get_ad_latlon(ad)
            if latlon:
                dist = self._calculate_distance(latlon[0], latlon[1])
                logger.debug(f"[AdScoringService] Ad#{ad.id} distance={dist:.2f}km")
                if dist <= 200:
                    eligible_ads.append(ad)
        logger.info(f"[AdScoringService] Proximity ads within 200km: {len(eligible_ads)}")
        return eligible_ads

    # -------------------------------------------------------------------
    # Cas général: scoring
    # -------------------------------------------------------------------
    def _get_eligible_ads(self):
        qs = Advertisement.objects.filter(
            status="ACTIVE",
            format=self.format,
            start_date__lte=self.now.date(),
            end_date__gte=self.now.date()
        ).select_related('related_activity', 'related_event')
        logger.debug(f"[AdScoringService] Eligible ads query: {qs.count()} found")
        return qs

    def _calculate_scores(self, ads):
        logger.debug("[AdScoringService] Calculating scores")
        scored_ads = []

        # déterminer la plus proche
        closest_id = None
        if self.user_lat is not None and self.user_lon is not None:
            distances = []
            for ad in ads:
                latlon = self._get_ad_latlon(ad)
                if latlon:
                    dist = self._calculate_distance(latlon[0], latlon[1])
                    distances.append((ad.id, dist))
                    logger.debug(f"[AdScoringService] Distance ad#{ad.id}: {dist:.2f}km")
            if distances:
                distances.sort(key=lambda x: x[1])
                closest_id = distances[0][0]
                logger.debug(f"[AdScoringService] Closest ad id: {closest_id}")

        for ad in ads:
            score = 0
            debug_reasons = []

            # Intérêts
            if self.user.has_data_consent:
                ad_categories = self._get_ad_categories(ad)
                user_interests = set(self.user.interests.values_list('id', flat=True))
                if user_interests.intersection(ad_categories):
                    score += SCORE_POINTS["INTEREST_MATCH"]
                    debug_reasons.append("interest_match")

            # Contexte heure/saison
            ctx_score = self._get_contextual_score(ad)
            if ctx_score:
                score += ctx_score
                debug_reasons.append(f"context+{ctx_score}")

            # Distance bonus
            if closest_id and ad.id == closest_id:
                score += SCORE_POINTS["PROXIMITY_BONUS"]
                debug_reasons.append("proximity_bonus")

            # Bonus
            if hasattr(ad, "bonus") and ad.bonus:
                score += ad.bonus
                debug_reasons.append(f"bonus+{ad.bonus}")

            logger.debug(
                f"[AdScoringService] Ad#{ad.id} scored {score} points ({', '.join(debug_reasons) or 'no match'})"
            )
            scored_ads.append({"ad_object": ad, "score": score})

        return scored_ads

    # -------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------
    def _get_ad_latlon(self, ad):
        if ad.related_activity and ad.related_activity.latitude and ad.related_activity.longitude:
            return ad.related_activity.latitude, ad.related_activity.longitude
        if ad.related_event and ad.related_event.latitude and ad.related_event.longitude:
            return ad.related_event.latitude, ad.related_event.longitude
        return None

    def _get_ad_categories(self, ad):
        if ad.related_activity:
            return set(ad.related_activity.category.values_list('id', flat=True))
        if ad.related_event:
            return set(ad.related_event.category.values_list('id', flat=True))
        return set()

    def _get_contextual_score(self, ad):
        context_score = 0
        hour = self.now.hour
        month = self.now.month

        cat_names = []
        if ad.related_activity:
            cat_names = ad.related_activity.category.values_list('name', flat=True)
        elif ad.related_event:
            cat_names = ad.related_event.category.values_list('name', flat=True)

        if 10.5 <= hour < 14 and any(c.lower() in ['restaurant', 'street food'] for c in cat_names):
            context_score += SCORE_POINTS["CONTEXT_TIME"]
        if hour >= 18 and any(c.lower() in ['bar', 'dancing', 'night life'] for c in cat_names):
            context_score += SCORE_POINTS["CONTEXT_TIME"]
        if month in [6, 7, 8, 9] and any(c.lower() in ['swimming'] for c in cat_names):
            context_score += SCORE_POINTS["CONTEXT_SEASON"]

        if context_score > 0:
            logger.debug(f"[AdScoringService] Context score for ad: {context_score}")

        return context_score

    def _calculate_distance(self, lat1, lon1):
        if self.user_lat is None or self.user_lon is None:
            return 99999
        R = 6371
        dlat = radians(lat1 - self.user_lat)
        dlon = radians(lon1 - self.user_lon)
        a = sin(dlat / 2)**2 + cos(radians(self.user_lat)) * cos(radians(lat1)) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c
