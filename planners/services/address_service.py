# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/models/address_service.py
# Author : Morice
# ---------------------------------------------------------------------------

import requests
import logging
from django.conf import settings
from ..models import AddressCache

logger = logging.getLogger('texasbuddy')

GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

def get_or_create_address_cache_from_place_id(address, place_id):
    """
    Vérifie en cache par place_id, sinon appelle Google Geocode et stocke.
    """
    # Check cache
    try:
        cache = AddressCache.objects.get(place_id=place_id)
        logger.info("[ADDRESS_CACHE_HIT] %s (%s)", address, place_id)
        return cache
    except AddressCache.DoesNotExist:
        logger.info("[ADDRESS_CACHE_MISS] Geocoding %s (%s)", address, place_id)

    # Call Google API
    params = {
        'place_id': place_id,
        'key': settings.GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(GOOGLE_GEOCODING_URL, params=params)
    data = response.json()

    if data['status'] != 'OK' or not data['results']:
        logger.error("[GEOCODING_FAILED] Place ID: %s, Address: %s, Response: %s", place_id, address, data)
        raise Exception(f"Failed to geocode place_id: {place_id} / address: {address}")

    result = data['results'][0]
    lat = result['geometry']['location']['lat']
    lng = result['geometry']['location']['lng']

    # Save new AddressCache
    cache = AddressCache.objects.create(
        place_id=place_id,
        address=address,
        latitude=lat,
        longitude=lng
    )

    logger.info("[GEOCODING_SUCCESS] %s -> (%s, %s)", address, lat, lng)

    return cache
