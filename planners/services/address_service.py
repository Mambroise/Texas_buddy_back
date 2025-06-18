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

def get_or_create_address_cache(address):
    # Check cache first
    try:
        cache = AddressCache.objects.get(address=address)
        logger.info("[ADDRESS_CACHE_HIT] %s", address)
        return cache
    except AddressCache.DoesNotExist:
        logger.info("[ADDRESS_CACHE_MISS] Geocoding %s", address)

    # Call Google API
    params = {
        'address': address,
        'region': 'us',
        'key': settings.GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(GOOGLE_GEOCODING_URL, params=params)
    data = response.json()

    if data['status'] != 'OK' or not data['results']:
        logger.error("[GEOCODING_FAILED] Address: %s, Response: %s", address, data)
        raise Exception(f"Failed to geocode address: {address}")

    result = data['results'][0]
    lat = result['geometry']['location']['lat']
    lng = result['geometry']['location']['lng']

    # Save new AddressCache
    cache = AddressCache.objects.create(
        address=address,
        latitude=lat,
        longitude=lng
    )

    logger.info("[GEOCODING_SUCCESS] %s → (%s, %s)", address, lat, lng)

    return cache
