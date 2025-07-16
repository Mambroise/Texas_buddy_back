
🔹 3️⃣ API REST (spec technique - ads_api.md)
markdown

# API Module Ads Texas Buddy

## Endpoints Mobile App

### GET /api/ads/
Retourne la liste des pubs actives
json
[
    {
        "id": 12,
        "title": "BBQ Tour Austin",
        "image_url": "https://cdn.texasbuddy.com/media/ads/12.jpg",
        "link_url": "https://bbqtour.com/austin-special"
    }
]



POST /api/ads/track-click/
json

{
    "ad_id": 12,
    "user_id": "optional"
}


POST /api/ads/conversion/
json

{
    "ad_id": 12,
    "user_id": "optional",
    "details": { "order_id": "X123", "amount": 99.00 }
}


Admin API (pour tableau de stats)
GET /api/ads/partners/

GET /api/ads/advertisements/

GET /api/ads/stats/?partner_id=X

json

{
    "impressions": 15499,
    "clicks": 345,
    "conversions": 21,
    "cpa_total": "$420.00"
}
