---------------------------------------------------------------------------
TEXAS BUDDY ( 2 0 2 5 )
---------------------------------------------------------------------------
Module : planners — API Endpoints
Author : Morice
---------------------------------------------------------------------------


Table des endpoints
Endpoint	Méthode	Description
/api/planners/trips/	GET/POST	Liste et création de Trips
/api/planners/trips/<id>/	GET/PUT/DELETE	Détail, modification ou suppression d'un Trip
/api/planners/trip-days/	GET/POST	Liste et création de TripDays
/api/planners/trip-days/<id>/	GET/PUT/DELETE	Détail, modification ou suppression d'un TripDay
/api/planners/trip-days/address-update/	POST	Mise à jour de l'adresse (reverse geocoding) pour un TripDay
/api/planners/trip-days/<trip_day_id>/sync/	POST	Synchronisation des TripSteps d’un TripDay
/api/planners/trip-steps/	GET/POST	Liste et création de TripSteps
/api/planners/trip-steps/<pk>/	DELETE	Suppression d’un TripStep
/api/planners/trip-steps/<pk>/move/	POST	Déplacement (changement d’horaire) d’un TripStep


Exemple détaillé : création d'un voyage. Le jours de voyage sont automatiquement créés.
Endpoint :
POST /api/planners/trips	

Exemple de payload envoyé depuis le mobile :
json

{
    "title": "Roadtrip Texas été 2025",
    "description": "Un voyage de 10 jours à travers le Texas",
    "start_date": "2025-07-10",
    "end_date": "2025-07-20"
}


Exemple détaillé : ajout de l'adresse au TripDay à partir de l'API google de géolocalisation.
Endpoint :
POST /api/planners/trip-days/address-update/	

Exemple de payload envoyé depuis le mobile :
json

{
  "trip_day_id": 4,
  "address": "The Loren Hotel Austin is 1211 W Riverside Dr, Austin, TX 78704, USA",
  "place_id": "ChIJQ4BhX-e1RIYR0Eg1T5vDE68"
}

Exemple détaillé : synchronisation des TripSteps
Endpoint :
POST /api/planners/trip-days/<trip_day_id>/sync/

Objectif :
Envoyer la liste complète des TripSteps pour une journée donnée (TripDay) — mise à jour ou création.
Si un step contient un id → update de l'objet existant.
Si un step n'a pas de id → création d'un nouveau TripStep.

Exemple de payload envoyé depuis le mobile :
json


{
  "steps": [
    {
      "id": 1,
      "start_time": "09:00:00",
      "estimated_duration_minutes": 90,
      "activity_id": 1,
      "note": "Petit-déjeuner à l'hôtel",
      "travel_mode": "walking",
      "travel_duration_minutes": 12,
      "travel_distance_meters": 900
    },
    {
      "id": 2,
      "start_time": "11:00:00",
      "estimated_duration_minutes": 60,
      "event_id": 1,
      "note": "Visite guidée du musée",
      "travel_mode": "transit",
      "travel_duration_minutes": 15,
      "travel_distance_meters": 3400
    },
    {
      "id":17,
      "start_time": "15:30:00",
      "estimated_duration_minutes": 120, 
      "activity_id": 2,
      "note": "Déjeuner en terrasse",
      "travel_mode": "driving",
      "travel_duration_minutes": 5,
      "travel_distance_meters": 3400
    }
  ]
}
Détails des champs :
Champ	Type	Obligatoire	Description
id	integer	optionnel	Identifiant de l'objet TripStep existant (si présent : update ; sinon : create)
start_time	string HH:MM:SS	oui	Heure de début (UTC ou locale à standardiser côté app)
estimated_duration_minutes	integer (minutes)	oui	Durée prévue en minutes
activity ou event	integer (id)	oui (l’un OU l’autre)	Soit activity, soit event, jamais les deux
note	string	optionnel	Note facultative associée à la TripStep

Rappel pour le client (exemple pour l'app mobile Flutter) :
Récupérer la liste actuelle des TripSteps via :
GET /api/planners/trip-steps/?trip_day=<trip_day_id>

Construire le payload de synchronisation en réutilisant les id des TripSteps existants.

Envoyer un POST /api/planners/trip-days/<trip_day_id>/sync/ avec l'ensemble des steps.

Ce que fait le backend :
✅ Pour chaque step envoyé :

Si id est présent et correspond à un TripStep existant → update des champs.

Si id est absent → création d'un nouveau TripStep.

Si un step contient un activity ET un event, une erreur sera retournée.

✅ Les horaires sont automatiquement ajustés pour éviter les chevauchements (cascade logic).

✅ Seuls les TripSteps appartenant au TripDay spécifié et au user connecté sont modifiables.

