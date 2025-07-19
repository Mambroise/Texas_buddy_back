
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
    "io_reference_number": "ABC-2025-001",
    "user_id": "optional"
}


POST /api/ads/conversion/
json

{
    "io_reference_number": "ABC-2025-001": 12,
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

=======================================================================================================
📌 API Notes – Advertisements Recommendation
URL :
GET /ads/recommend/

Name (Django URL name) :
recommend-ad

Auth required : ✅ Oui (l’utilisateur doit être authentifié via un token ou session)

Description :
Cette endpoint renvoie une liste d’annonces recommandées pour l’utilisateur authentifié en fonction :

du format publicitaire demandé (fmt),

et éventuellement de la position GPS (lat, lng).

Pour chaque publicité renvoyée, une impression est automatiquement tracée dans le système de logs publicitaires.

🔑 Query Parameters
Paramètre	Type	Requis	Description
fmt	string	✅	Format publicitaire attendu. Exemples : interstitial, native, push.
lat	float	❌	Latitude actuelle de l’utilisateur. Permet d’améliorer le scoring géolocalisé.
lng	float	❌	Longitude actuelle de l’utilisateur. Permet d’améliorer le scoring géolocalisé.

✅ Comportement
Vérifie que fmt est fourni, sinon répond en erreur 400 Bad Request.

Valide lat et lng si présents, sinon les ignore.

Calcule la liste des annonces les plus pertinentes via le service AdScoringService.

Trace automatiquement une impression pour chaque annonce retournée grâce à TrackImpression.

Retourne la liste d’annonces sérialisées.

📥 Exemple de requête
http
Copier
Modifier
GET /ads/recommend/?fmt=native&lat=32.7767&lng=-96.7970
Authorization: Bearer <token>
📤 Exemple de réponse
json

[
  {
    "id": 12,
    "title": "Visitez le Musée d'Art Moderne",
    "image_url": "https://example.com/media/ad_12.jpg",
    "format": "native",
    "target_url": "https://example.com/musee",
    "distance_km": 1.2
  },
  {
    "id": 34,
    "title": "Concert Live au Parc",
    "image_url": "https://example.com/media/ad_34.jpg",
    "format": "native",
    "target_url": "https://example.com/concert",
    "distance_km": 2.7
  }
]
⚠️ Erreurs possibles
Code	Signification	Corps de réponse
400	Paramètre fmt manquant ou coordonnées invalides	{"error": "Ad format is required."} ou {"error": "Invalid latitude or longitude."}
401	Utilisateur non authentifié	{"detail": "Authentication credentials were not provided."}

📝 Notes techniques
AdvertisementsRecommendationView utilise :

AdScoringService pour déterminer les meilleures publicités selon :

la géolocalisation (lat, lon),

l’utilisateur (request.user),

le format (fmt).

TrackImpression pour enregistrer automatiquement une impression sur chaque publicité renvoyée.

Le serializer utilisé est AdvertisementSerializer.

Les logs (logger.info, logger.debug, logger.exception) permettent de suivre les requêtes et la traçabilité des impressions.

