# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : planners/services/google_places.py
# Author : Morice (refactor w/ city + TX bias, safe upserts)
# ---------------------------------------------------------------------------

from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from ..models import AddressCache


# --- Config / Const --------------------------------------------------------

API_KEY = settings.GOOGLE_PLACES_API_KEY
PLACES_BASE = "https://maps.googleapis.com/maps/api/place"
AUTOCOMPLETE_URL = f"{PLACES_BASE}/autocomplete/json"
DETAILS_URL = f"{PLACES_BASE}/details/json"

# Borne approximatives du Texas (min_lng, min_lat, max_lng, max_lat)
TEXAS_BOUNDS: Tuple[float, float, float, float] = (-106.6456, 25.8371, -93.5083, 36.5007)

# Viewports approximatifs des grandes villes (biais fort)
CITY_BOUNDS: Dict[str, Tuple[float, float, float, float]] = {
    "dallas":      (-97.0190, 32.6170, -96.4637, 33.0235),
    "austin":      (-97.9367, 30.0980, -97.5333, 30.4889),
    "houston":     (-95.9099, 29.4706, -95.0145, 30.1547),
    "san antonio": (-98.7960, 29.1982, -98.2211, 29.7429),
    "fort worth":  (-97.5151, 32.5206, -97.0935, 32.9646),
}


# --- Exceptions ------------------------------------------------------------

class GooglePlacesError(RuntimeError):
    pass


def _must_api_key():
    if not API_KEY:
        raise GooglePlacesError("GOOGLE_PLACES_API_KEY is not configured")


# --- Helpers géo / filtrage ------------------------------------------------

def _bounds_for_city(city: Optional[str]) -> Tuple[float, float, float, float]:
    if not city:
        return TEXAS_BOUNDS
    key = (city or "").strip().lower()
    return CITY_BOUNDS.get(key, TEXAS_BOUNDS)


def _center_of_bounds(bounds: Tuple[float, float, float, float]) -> Tuple[float, float]:
    min_lng, min_lat, max_lng, max_lat = bounds
    return ( (min_lat + max_lat) / 2.0, (min_lng + max_lng) / 2.0 )


def _approx_radius_m(bounds: Tuple[float, float, float, float]) -> int:
    # Rayon ≈ moitié de la plus grande dimension (mètres; approximation suffisante pour un bias)
    min_lng, min_lat, max_lng, max_lat = bounds
    dlat_m = (max_lat - min_lat) * 111_000
    dlng_m = (max_lng - min_lng) * 92_000   # approx pour TX
    return int(max(dlat_m, dlng_m) / 2.0)


def _looks_like_in_state(text: str, state_code: str = "TX") -> bool:
    s = (text or "").lower()
    code = (state_code or "").lower()
    return (f", {code}" in s) or s.endswith(f" {code}") or (f" {code},") in s


def _looks_like_in_city(text: str, city: Optional[str]) -> bool:
    if not city:
        return True
    s = (text or "").lower()
    c = (city or "").strip().lower()
    return c in s


def _filter_predictions(preds: List[Dict[str, Any]], city: Optional[str], state: str = "TX") -> List[Dict[str, Any]]:
    # Priorité: même ville + même état; sinon fallback: état uniquement
    in_city_state: List[Dict[str, Any]] = []
    in_state_only: List[Dict[str, Any]] = []

    for p in preds:
        desc = (p.get("formatted_address") or p.get("description") or "")
        if _looks_like_in_state(desc, state):
            if _looks_like_in_city(desc, city):
                in_city_state.append(p)
            else:
                in_state_only.append(p)

    return in_city_state or in_state_only or preds


# --- API calls -------------------------------------------------------------

def google_autocomplete(
    q: str,
    lang: str,
    city: Optional[str] = None,
    region_bias: str = "us",
    state_bias: Optional[str] = "TX",
    session_token: Optional[str] = None,
    limit: int = 8,
) -> List[Dict[str, Any]]:
    """
    Appelle Places Autocomplete; renvoie une liste normalisée:
      {place_id, name, formatted_address, city, state_code, country_code, lat=None, lng=None, source='google'}
    NB: lat/lng ne sont pas fournis par Autocomplete => None ici (on les aura via Details).
    Un biais géographique est appliqué: ville -> Texas (fallback).
    """
    _must_api_key()

    # Bias géographique
    bounds = _bounds_for_city(city)
    lat_center, lng_center = _center_of_bounds(bounds)
    radius_m = _approx_radius_m(bounds)

    params = {
        "input": q,
        "language": lang or "en",
        "key": API_KEY,
        "components": f"country:{(region_bias or 'us').lower()}",
        # Bias via location + radius (autocomplete REST l'accepte, même si « strictbounds » est JS-only)
        "location": f"{lat_center:.6f},{lng_center:.6f}",
        "radius": str(radius_m),
        "types": "establishment",  # ou 'geocode' selon tes besoins
    }
    if session_token:
        params["sessiontoken"] = session_token

    try:
        resp = requests.get(AUTOCOMPLETE_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise GooglePlacesError(f"Autocomplete request failed: {e}") from e

    status = data.get("status")
    if status not in ("OK", "ZERO_RESULTS"):
        raise GooglePlacesError(f"Autocomplete error: {status} {data.get('error_message')}")

    preds = data.get("predictions", [])
    out: List[Dict[str, Any]] = []

    for p in preds:
        place_id = p.get("place_id")
        sf = p.get("structured_formatting") or {}
        main_text = sf.get("main_text") or ""
        # 'description' contient généralement "Nom, Rue, Ville, TX, USA"
        description = p.get("description") or ""
        secondary = sf.get("secondary_text") or ""
        formatted = description or ", ".join(filter(None, [main_text, secondary]))

        out.append({
            "place_id": place_id,
            "name": main_text,
            "formatted_address": formatted,
            "lat": None,
            "lng": None,
            "city": city,  # on injecte la ville demandée (meilleur merge côté front)
            "state_code": (state_bias or "TX"),
            "country_code": (region_bias or "us").upper(),
            "source": "google",
            # 'components': {}  # tu peux parser plus finement si besoin
        })

    # Filtre côté serveur pour garder TX (+ ville si possible)
    filtered = _filter_predictions(out, city=city, state=(state_bias or "TX"))
    return filtered[:limit]


def google_place_details(
    place_id: str,
    lang: str,
    session_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Appelle Place Details; renvoie le payload Google 'result'.
    """
    _must_api_key()
    params = {
        "place_id": place_id,
        "language": lang or "en",
        "key": API_KEY,
        "fields": "place_id,name,formatted_address,geometry,address_components",
    }
    if session_token:
        params["sessiontoken"] = session_token

    try:
        resp = requests.get(DETAILS_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise GooglePlacesError(f"Place Details request failed: {e}") from e

    if data.get("status") != "OK":
        raise GooglePlacesError(f"Place Details error: {data.get('status')} {data.get('error_message')}")
    return data.get("result") or {}


# --- Upserts ---------------------------------------------------------------

def upsert_places(predictions: List[Dict[str, Any]], ttl_days: int = 21) -> None:
    """
    Reçoit des items type Autocomplete (souvent SANS lat/lng).
    - Si lat/lng absents -> on NE crée PAS (évite NOT NULL).
      On tente juste une mise à jour légère si la ligne existe déjà.
    - Si lat/lng présents -> update_or_create normal.
    """
    now = timezone.now()
    expires = now + timedelta(days=ttl_days)

    for p in predictions:
        pid = p.get('place_id')
        if not pid:
            continue

        name = p.get('name') or p.get('primary_text') or p.get('description')
        formatted = p.get('formatted_address') or p.get('secondary_text') or p.get('description')
        lang = p.get('language') or 'en'
        city = p.get('city')
        state = p.get('state_code')
        country = p.get('country_code') or 'US'
        comps = p.get('components') or {}

        lat = p.get('lat')
        lng = p.get('lng')

        # Autocomplete n'a pas lat/lng -> on SKIP la création
        if lat is None or lng is None:
            AddressCache.objects.filter(place_id=pid).update(
                name=name,
                formatted_address=formatted,
                language=lang,
                city=city, state_code=state, country_code=country,
                components=comps,
                source='google',
                refreshed_at=now,
                expires_at=expires,
            )
            continue

        try:
            lat = float(lat)
            lng = float(lng)
        except (TypeError, ValueError):
            # Valeurs invalides -> ne pas créer
            continue

        AddressCache.objects.update_or_create(
            place_id=pid,
            defaults=dict(
                name=name,
                formatted_address=formatted,
                lat=lat,
                lng=lng,
                language=lang,
                city=city, state_code=state, country_code=country,
                components=comps,
                source='google',
                refreshed_at=now,
                expires_at=expires,
            ),
        )


def upsert_place_details(details: Dict[str, Any]) -> AddressCache:
    """
    Upsert “complet” depuis Details (lat/lng + address_components).
    """
    pid = details.get("place_id") or ""
    name = (details.get("name") or "")[:255]
    formatted = (details.get("formatted_address") or "")[:512]

    geom = (details.get("geometry") or {})
    loc = geom.get("location") or {}
    lat = loc.get("lat")
    lng = loc.get("lng")

    # Cast robustes (évite longitudes astronomiques)
    try:
        lat = float(lat) if lat is not None else None
        lng = float(lng) if lng is not None else None
    except (TypeError, ValueError):
        lat = None
        lng = None

    comps = details.get("address_components") or []
    city, state_code, country_code = parse_components(comps)

    obj, _ = AddressCache.objects.update_or_create(
        place_id=pid,
        defaults={
            "name": name,
            "formatted_address": formatted,
            "lat": lat,
            "lng": lng,
            "city": city,
            "state_code": state_code,
            "country_code": country_code or "US",
            "language": (settings.LANGUAGE_CODE if hasattr(settings, "LANGUAGE_CODE") else "en"),
            "components": {},
            "source": "google",
            "refreshed_at": timezone.now(),
            "expires_at": timezone.now() + timedelta(days=21),
        },
    )
    return obj


def parse_components(components: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extrait (city, state_code, country_code) depuis address_components.
    """
    city = state = country = None
    for c in components:
        types = c.get("types", [])
        if "locality" in types or "postal_town" in types:
            city = c.get("long_name")
        if "administrative_area_level_1" in types:
            state = c.get("short_name")
        if "country" in types:
            country = c.get("short_name")
    return city, state, country
