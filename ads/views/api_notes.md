
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



POST /api/ads/click/
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

🎯 Endpoint: GET /ads/interstitial/
📝 Utilité
Cet endpoint sert à sélectionner et renvoyer une publicité interstitielle prioritaire (format plein écran), affichée juste après le chargement de la page d’accueil (la carte en temps réel).
L’objectif est :

de cibler la publicité en fonction de la position géographique de l’utilisateur,

de prioriser les publicités marquées comme “prioritaires” (PriorityAd) sur une période active,

et d’enregistrer automatiquement une impression lorsque la publicité est renvoyée.

C’est donc un outil de monétisation et de diffusion dynamique.

⚙️ Fonctionnement détaillé
Requête attendue

Méthode : GET

Paramètres query obligatoires :

lat: latitude de l’utilisateur.

lng: longitude de l’utilisateur.

Optionnel :

Authentification (request.user) si l’utilisateur est connecté (sinon user = None).

Filtrage des publicités prioritaires

On sélectionne tous les enregistrements PriorityAd :

qui sont actifs (is_active=True),

dont la publicité associée (advertisement) est :

de format interstitial,

dont la date de début est passée,

et la date de fin pas encore expirée.

Sélection de la publicité la plus proche

Pour chaque publicité prioritaire :

Si elle est liée à un événement (related_event) avec coordonnées, on calcule la distance haversine.

Si elle est liée à une activité (related_activity) avec coordonnées, on calcule la distance haversine.

On retient la distance la plus petite entre activité et événement.

On conserve la publicité la plus proche de l’utilisateur parmi toutes les candidates.

Création d’une impression

Si une publicité est trouvée :

On crée un enregistrement AdImpression (journalisation de la diffusion).

On retourne la publicité sérialisée (JSON complet via AdvertisementSerializer).

Réponse si aucune publicité

Si aucune publicité prioritaire ne correspond ou qu’aucune n’est géolocalisée :

On retourne un 204 No Content avec un message indiquant qu’il n’y a rien à afficher.

📤 Réponses possibles
200 OK

json

{
  "id": 1,
  "title": "festival vin austin",
  "image": "/media/ads/Maurice_Ambroise.jpg",
  "link_url": "https://furkot.fr/",
  "start_date": "2025-06-27",
  "end_date": "2025-07-24",
  "related_activity": null,
  "related_event": 2,
  "related_activity_detail": null,
  "related_event_detail": {
    "id": 2,
    "name": "Austin Food + Wine Festival",
    "description": "The Austin Food + Wine Festival returns November 7–9, 2025 at Auditorium Shores in Austin, TX. Enjoy artisanal food, wine, beer and spirits from top-rated purveyors, live chef demos, tasting sessions, a Fire Pit featuring barbecue from pitmasters, and an electrifying view of the Austin skyline.",
    "start_datetime": "2025-11-07T12:00:00Z",
    "end_datetime": "2025-11-09T22:00:00Z",
    "location": "Auditorium Shores",
    "city": "Austin",
    "state": "Texas",
    "place_id": "ChIJEcb8OQW1RIYRmfmMOE9aPQs",
    "latitude": 30.2523,
    "longitude": -97.7514,
    "category": [
      {
        "id": 4,
        "name": "wine bar",
        "icon": "fa-wine-glass",
        "description": ""
      },
      {
        "id": 9,
        "name": "food",
        "icon": "fa-plate-wheat",
        "description": ""
      },
      {
        "id": 15,
        "name": "music/concert",
        "icon": "fa-guitar",
        "description": ""
      },
      {
        "id": 8,
        "name": "drinks",
        "icon": "fa-glass-cheers",
        "description": ""
      }
    ],
    "website": "https://www.austinfoodandwinefestival.com/",
    "image": null,
    "price": 125.0,
    "duration": "00:00:12",
    "staff_favorite": false,
    "is_public": true,
    "created_at": "2025-06-14T09:14:49.732792Z",
    "promotions": [
      {
        "id": 3,
        "title": "summer sales",
        "description": "test en",
        "discount_type": "percentage",
        "amount": "19.98",
        "start_date": "2025-11-08",
        "end_date": "2025-11-09",
        "is_active": true
      }
    ],
    "current_promotion": null,
    "has_promotion": false
  },
  "cpm_price": null,
  "cpc_price": "0.20",
  "cpa_price": null,
  "forfait_price": null,
  "impressions_count": 0,
  "clicks_count": 0,
  "conversions_count": 0,
  "created_at": "2025-06-27T21:42:19.957667Z",
  "partner": {
    "id": 1,
    "name": "Claudia hepburn",
    "contact_email": "claudi.hepburn@bigben.com",
    "phone": "",
    "website": "https://www.nps.gov/bibe/index.htm",
    "contract_signed_date": "2025-06-27",
    "contract_type": "CPC",
    "is_active": true,
    "created_at": "2025-06-27T21:34:25.873232Z"
  }
}
(dépend des champs de AdvertisementSerializer)

204 No Content

json

{
  "message": "No interstitial ad available."
}
400 Bad Request

json

{
  "error": "Missing lat/lng"
}
🧠 Notes techniques importantes
Distance calculée avec la formule de Haversine pour obtenir la distance en kilomètres.

Sécurité : pas d’authentification obligatoire, mais si l’utilisateur est identifié, l’impression est rattachée.

Impact analytics :

Chaque affichage crée une ligne AdImpression (pour la facturation CPM).

Fallback : il n’y a pas de repli automatique vers une publicité non prioritaire dans cette vue (ce comportement peut être ajouté plus tard).

✨ Cas d’usage
App mobile : après la géolocalisation initiale, interroger cet endpoint pour récupérer une publicité interstitielle à afficher en plein écran.

Si aucune publicité prioritaire n’est disponible, passer à un autre contenu (par exemple un événement national ou une activité générique).


🌐 Endpoint
python
Copy
Edit
path('push/', PushNotificationAdView.as_view(), name='push-ads')
📌 Fonctionnement du endpoint
URL : /api/ads/push/ (ou selon le prefix API que tu as configuré)

Méthode HTTP : GET

Nom Django : push-ads

Paramètres requis (query parameters) :

lat : latitude de l’utilisateur (float)

lng : longitude de l’utilisateur (float)

Ce endpoint sert à récupérer les publicités push actives autour de l’utilisateur, triées par proximité.

🧩 Vue PushNotificationAdView
📘 Résumé
Cette vue hérite de APIView (DRF) et expose une méthode GET.
Elle :
✅ récupère la position de l’utilisateur,
✅ filtre les publicités push actives et valides,
✅ calcule la distance,
✅ retourne la liste triée des publicités proches.

🛠️ Étapes de fonctionnement
1️⃣ Validation des paramètres
Récupère lat et lng dans request.query_params.

Si l’un des deux est absent, retourne :

json
Copy
Edit
{"error": "Missing lat/lng"}
avec 400 Bad Request.

2️⃣ Filtrage des publicités actives
Recherche toutes les Advertisement dont :

format = "push"

start_date ≤ aujourd’hui

end_date ≥ aujourd’hui

Charge en même temps les objets liés (related_event, related_activity) grâce à .select_related(...).

3️⃣ Parcours et enrichissement
Pour chaque publicité :

Si liée à un événement :

Vérifie la présence de latitude/longitude.

Calcule la distance avec la fonction haversine.

Ignore si distance > 2000 km.

Crée un dictionnaire contenant :

type = event

titre de l’événement

dates de début et de fin.

Si liée à une activité unique :

Vérifie si is_unique est True et présence de latitude/longitude.

Calcule la distance.

Ignore si distance > 200 km.

Crée un dictionnaire similaire (sans date).

Toutes les publicités valides sont stockées dans enriched_ads.

4️⃣ Tri des publicités
Trie la liste enriched_ads par distance croissante.

5️⃣ Formatage JSON
Transforme chaque publicité enrichie en un objet JSON :

json
Copy
Edit
{
  "id": ...,
  "format": "push",
  "title": ...,
  "image_url": ...,
  "distance_km": ...,
  "object_type": "event" ou "activity",
  "object_id": ...,
  "object_title": ...,
  "start_date": ... (si event),
  "end_date": ... (si event)
}
Les dates ne sont ajoutées que si l’objet est un événement.

6️⃣ Retour de la réponse
Si aucune publicité n’est trouvée :

json
Copy
Edit
{"message": "No push ads available."}
avec 204 No Content.

Sinon :

json
Copy
Edit
[
  { publicité 1 },
  { publicité 2 },
  ...
]
avec 200 OK.

⚙️ Fonction utilitaire haversine
Cette fonction calcule la distance (en km) entre deux coordonnées GPS avec la formule de Haversine :

python

def haversine(lat1, lon1, lat2, lon2):
    R = 6371 km
    ...
    return distance_km
🧠 Exemple d’appel API
swift

GET /api/ads/push/?lat=30.2523&lng=-93.7514
Réponse si publicités trouvées :

json

[
  {
    "id": 42,
    "format": "push",
    "title": "Promo Festival",
    "image_url": "/media/ads/festival.jpg",
    "distance_km": 12.4,
    "object_type": "event",
    "object_id": 7,
    "object_title": "Festival de musique",
    "start_date": "2025-07-01T18:00:00Z",
    "end_date": "2025-07-05T23:00:00Z"
  },
  {
    "id": 43,
    "format": "push",
    "title": "Réduction Musée",
    "image_url": "/media/ads/museum.jpg",
    "distance_km": 45.1,
    "object_type": "activity",
    "object_id": 15,
    "object_title": "Musée des sciences"
  }
]
✨ Points importants
Les distances sont arrondies à 1 chiffre après la virgule.

Les publicités incomplètes (manque lat/lng) sont ignorées.

Les événements/activités trop éloignés (>2000 km) sont ignorés.

La réponse est toujours triée par distance croissante.



