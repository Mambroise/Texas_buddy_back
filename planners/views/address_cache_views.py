# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/views/address_cache_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.utils.translation import gettext_lazy as _

import logging
from uuid import uuid4
from django.conf import settings
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..services.address_cache_service import serialize, merge_by_place_id  # si tu les as ailleurs, adapte
from ..services.address_cache_service import search_in_tx
from ..services.google_places import (
    google_autocomplete,
    upsert_places,
    google_place_details,
    upsert_place_details,
)

logger = logging.getLogger('texasbuddy')

# --- ADDRESS UPDATE : POST avec RateLimitedAPIView ---

def _session_key(request, city: str) -> str:
    user_id = getattr(request.user, "id", None) or "anon"
    return f"places:session:{user_id}:{(city or 'tx').lower()}"

def _get_or_create_session_token(request, city: str) -> str:
    key = _session_key(request, city)
    token = cache.get(key)
    if not token:
        token = str(uuid4())
        cache.set(key, token, settings.PLACES_SESSION_TTL_SECONDS)
    return token

@method_decorator(ratelimit(key='ip', rate='100/10m', method='GET', block=True), name='dispatch')
class AddressSearchTXView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

    def get(self, request):
        city = (request.query_params.get("city") or "").strip()
        q = (request.query_params.get("q") or "").strip()
        lang = request.query_params.get("lang", "en")
        limit = int(request.query_params.get("limit", 8))

        if not city:
            return Response({"detail": "city is required"}, status=status.HTTP_400_BAD_REQUEST)
        if len(q) < 3:
            return Response([], status=status.HTTP_200_OK)

        # 1) Cache d'abord
        cache_results = search_in_tx(city, q, lang, limit=limit)
        if len(cache_results) >= settings.ADDRESS_CACHE_MIN_RESULTS:
            logger.info("[ADDRESS_SEARCH] cache_hit city=%s q=%s n=%s", city, q, len(cache_results))
            return Response(serialize(cache_results))

        # 2) Session token côté serveur (si absent)
        session_token = request.query_params.get("token") or _get_or_create_session_token(request, city)

        # 3) Fallback Google Autocomplete
        try:
            g_results = google_autocomplete(
                q=q,
                lang=lang,
                city=city,
                region_bias=settings.PLACES_REGION_BIAS,
                state_bias=settings.PLACES_STATE_BIAS,
                session_token=session_token,
                limit=limit,
            )
        except Exception as e:
            logger.exception("[ADDRESS_SEARCH] google_autocomplete_failed city=%s q=%s error=%s", city, q, e)
            # On n'échoue pas: renvoie simplement le cache (peut être vide)
            return Response(serialize(cache_results), status=status.HTTP_200_OK)

        # 4) Upsert Google → enrichit le cache
        upsert_places(g_results, ttl_days=21)

        merged = merge_by_place_id(cache_results, g_results, limit=limit)
        logger.info("[ADDRESS_SEARCH] cache_merge city=%s q=%s cache=%s google=%s merged=%s",
                    city, q, len(cache_results), len(g_results), len(merged))
        return Response(merged, status=status.HTTP_200_OK)

class AddressSelectView(APIView):
    """
    POST /api/address/select/
    body: { "place_id": "...", "city": "Dallas" }
    Retourne l'adresse normalisée + ID du cache
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        place_id = (request.data.get("place_id") or "").strip()
        city = (request.data.get("city") or "").strip()
        lang = request.data.get("lang") or request.LANGUAGE_CODE or "en"

        if not place_id:
            return Response({"detail": "place_id required"}, status=status.HTTP_400_BAD_REQUEST)

        session_token = _get_or_create_session_token(request, city or "tx")
        try:
            details = google_place_details(place_id=place_id, lang=lang, session_token=session_token)
            ac = upsert_place_details(details)
        except Exception as e:
            logger.exception("[ADDRESS_SELECT] details_failed place_id=%s city=%s error=%s", place_id, city, e)
            return Response({"detail": "Failed to resolve place details"}, status=status.HTTP_502_BAD_GATEWAY)

        # Optionnel: purge de session (sinon TTL expirera)
        # cache.delete(_session_key(request, city or "tx"))

        return Response({
            "address_cache_id": ac.id,
            "place_id": ac.place_id,
            "formatted_address": ac.formatted_address,
            "lat": ac.lat, "lng": ac.lng,
            "city": ac.city, "state_code": ac.state_code, "country_code": ac.country_code,
            "source": ac.source,
        }, status=status.HTTP_200_OK)
