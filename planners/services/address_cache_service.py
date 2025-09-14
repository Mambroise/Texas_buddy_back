# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/models/address_cache_service.py
# Author : Morice
# ---------------------------------------------------------------------------

# app/services/address_search.py
from django.db.models import F, Q, Value, FloatField, Case, When
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from django.utils import timezone
from ..models import AddressCache


def serialize(items):
    return [
        {
            "place_id": it.place_id,
            "name": it.name,
            "formatted_address": it.formatted_address,
            "lat": it.lat,
            "lng": it.lng,
            "city": it.city,
            "state_code": it.state_code,
            "country_code": it.country_code,
            "source": it.source,
            "address_cache_id": getattr(it, "id", None),  # dispo pour source=cache
        }
        for it in items
    ]

def merge_by_place_id(cache_items, google_items, limit=8):
    seen = set()
    out = []
    for it in cache_items:
        if it.place_id not in seen:
            out.append({
              "place_id": it.place_id, "name": it.name,
              "formatted_address": it.formatted_address,
              "lat": it.lat, "lng": it.lng,
              "city": it.city, "state_code": it.state_code, "country_code": it.country_code,
              "source": it.source
            })
            seen.add(it.place_id)
    for g in google_items:
        if g["place_id"] not in seen:
            out.append(g); seen.add(g["place_id"])
        if len(out) >= limit: break
    return out[:limit]

def search_in_tx(city: str, query: str, language: str, limit: int = 8):
    city_norm = (city or "").strip()
    q_norm = (query or "").strip()
    if len(q_norm) < 3:
        return []

    vector = (SearchVector('name', weight='A') +
              SearchVector('formatted_address', weight='B'))

    sq = SearchQuery(q_norm, search_type='plain')

    base = (AddressCache.objects
            .filter(country_code='US', state_code='TX')
            .filter(Q(language=language) | Q(language='en')))

    # FTS + trigram
    qs = (base
          .annotate(
              rank=SearchRank(vector, sq),
              sim=TrigramSimilarity('name', q_norm) + TrigramSimilarity('formatted_address', q_norm),
              city_boost=Case(
                  When(city__istartswith=city_norm, then=Value(0.60)),
                  default=Value(0.0),
                  output_field=FloatField(),
              ),
              state_boost=Value(0.25, output_field=FloatField()),   # Texas permanent
          )
          .filter(Q(rank__gt=0.05) | Q(sim__gt=0.12))
          .annotate(score=F('rank') + F('sim') + F('city_boost') + F('state_boost'))
          .order_by('-score')[:limit])

    # Stats cache
    AddressCache.objects.filter(pk__in=[x.pk for x in qs]).update(
        hit_count=F('hit_count') + 1,
        last_used_at=timezone.now()
    )
    return list(qs)
