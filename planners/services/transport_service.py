# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : planners/services/transport_service.py
# Author : Morice 
# ---------------------------------------------------------------------------

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import requests

DM_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"

def _cache_key(lat1, lng1, lat2, lng2, mode, lang):
    return f"dm:{mode}:{lang}:{round(lat1,5)},{round(lng1,5)}->{round(lat2,5)},{round(lng2,5)}"

def estimate_travel_minutes_meters(*, origin, destination, mode="driving", lang="en"):
    """
    origin = {"lat": float, "lng": float}
    destination = {"lat": float, "lng": float}
    returns: (minutes:int, meters:int)
    """
    k = _cache_key(origin["lat"], origin["lng"], destination["lat"], destination["lng"], mode, lang)
    cached = cache.get(k)
    if cached:
        return cached

    params = {
        "origins": f'{origin["lat"]},{origin["lng"]}',
        "destinations": f'{destination["lat"]},{destination["lng"]}',
        "mode": mode,
        "departure_time": "now",          # duration_in_traffic si dispo
        "language": lang,
        "key": settings.GOOGLE_MAPS_WEB_SERVICE_KEY,
    }
    r = requests.get(DM_URL, params=params, timeout=7)
    r.raise_for_status()
    data = r.json()

    rows = data.get("rows", [])
    if not rows or not rows[0].get("elements"):
        raise ValueError("Distance Matrix: empty result")

    e = rows[0]["elements"][0]
    status = e.get("status")
    if status != "OK":
        raise ValueError(f"Distance Matrix element status={status}")

    dur_sec = (e.get("duration_in_traffic") or e.get("duration") or {}).get("value", 0)
    dist_m  = (e.get("distance") or {}).get("value", 0)

    minutes = int(round(dur_sec / 60)) if dur_sec else 0
    meters  = int(dist_m)

    # petite normalisation
    if minutes < 0: minutes = 0
    if meters  < 0: meters = 0

    out = (minutes, meters)
    cache.set(k, out, timeout=getattr(settings, "DISTANCE_CACHE_TTL_SECONDS", 1800))
    return out
