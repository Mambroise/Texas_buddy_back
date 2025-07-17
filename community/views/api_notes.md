# 📌 API Notes – Module Community (Reviews)

Cette documentation décrit les endpoints liés aux **avis (reviews)** sur les activités et événements dans l’application Texas Buddy.

---

## 🔑 Authentification

🔒 **Toutes les routes nécessitent un utilisateur authentifié** (via JWT ou autre système configuré dans ton projet).  
- Header obligatoire :  
`Authorization: Bearer <access_token>`

---

## 📍 Endpoints disponibles

### ➡️ 1. Lister les avis d’une activité ou d’un événement

**GET** `/api/community/reviews/`

#### Paramètres Query (au moins un requis) :

| Paramètre      | Type   | Obligatoire | Description |
|----------------|--------|-------------|-------------|
| `activity_id`  | int    | ✅ si `event_id` non fourni | Lister les avis liés à une activité spécifique. |
| `event_id`     | int    | ✅ si `activity_id` non fourni | Lister les avis liés à un événement spécifique. |
| `min_rating`   | float  | ❌ | Filtrer pour ne récupérer que les avis dont la note est supérieure ou égale. |
| `max_rating`   | float  | ❌ | Filtrer pour ne récupérer que les avis dont la note est inférieure ou égale. |
| `page`         | int    | ❌ | Pagination : numéro de page. |
| `page_size`    | int    | ❌ | Pagination : nombre d’éléments par page. (max 100) |

#### Exemple de requête :
GET /api/community/reviews/?activity_id=42&min_rating=3&page=1&page_size=5
Authorization: Bearer <token>


#### Réponse (200) :
```json
{
  "count": 12,
  "next": "http://.../reviews/?activity_id=42&page=2",
  "previous": null,
  "results": [
    {
      "id": 101,
      "user": {
        "id": 7,
        "email": "jane@example.com",
        "username": "Jane"
      },
      "rating": 4,
      "comment": "Super activité, je recommande !",
      "created_at": "2025-07-15T08:30:00Z"
    },
    {
      "id": 102,
      "user": {
        "id": 9,
        "email": "paul@example.com",
        "username": "Paul"
      },
      "rating": 5,
      "comment": "",
      "created_at": "2025-07-14T19:10:00Z"
    }
  ]
}
Codes de réponse :
✅ 200 OK – Liste des avis paginée.

⚠️ 400 Bad Request – Ni activity_id ni event_id fourni, ou les deux à la fois.

➡️ 2. Créer un nouvel avis
POST /api/community/reviews/

Corps JSON :
Champ	      Type	   Obligatoire	  Description
target_type	string	✅	            "activity" ou "event".
target_id	  int	      ✅	          ID de l’activité ou de l’événement.
rating	    int	        ✅       	Note entre 1 et 5.
comment	   string	    ❌	          Commentaire facultatif.

Exemple de requête :
pgsql
Copier
Modifier
POST /api/community/reviews/
Authorization: Bearer <token>
Content-Type: application/json

{
  "target_type": "activity",
  "target_id": 42,
  "rating": 5,
  "comment": "Incroyable expérience !"
}
Réponse (201) :
json
Copier
Modifier
{
  "id": 123,
  "user": {
    "id": 7,
    "email": "jane@example.com",
    "username": "Jane"
  },
  "rating": 5,
  "comment": "Incroyable expérience !",
  "created_at": "2025-07-15T09:05:00Z"
}
Codes de réponse :
✅ 201 Created – Avis créé.

⚠️ 400 Bad Request – Paramètre manquant ou invalide.

🔒 401 Unauthorized – Non authentifié.

🛠️ Notes techniques
📌 Pagination : par défaut page_size=10, modifiable via ?page_size=<int> (max 100).

📌 Filtrage :

min_rating et max_rating peuvent être combinés pour un intervalle :
?min_rating=3&max_rating=4

📌 Throttling :

GET et POST utilisent des throttles custom (GetRateLimitedAPIView, PostRateLimitedAPIView).

Les limites sont définies dans core.throttles.

✅ Checklist pour l’intégration front-end
 Authentification via header Authorization.

 Passer soit activity_id, soit event_id pour le listing.

 Utiliser les filtres min_rating et max_rating pour affiner.

 Gérer la pagination (count, next, previous, results).

 POST avec les champs target_type, target_id, rating, et optionnellement comment.

✨ Exemples rapides
Lister les avis pour l’activité 42 :

swift
Copier
Modifier
GET /api/community/reviews/?activity_id=42
Lister les avis pour l’événement 7 avec note ≥ 4 :

swift
Copier
Modifier
GET /api/community/reviews/?event_id=7&min_rating=4
Créer un avis pour l’activité 42 :

swift
Copier
Modifier
POST /api/community/reviews/
{
  "target_type": "activity",
  "target_id": 42,
  "rating": 5,
  "comment": "Top !"
}
🔮 Évolutions futures possibles
✅ Mise à jour ou suppression d’un avis par son auteur.

✅ Ajout d’un champ photos ou tags pour enrichir les avis.

✅ Système de votes (utile/inutile) sur les avis.

✨ Modifier une review existante
URL : PUT /api/community/reviews/<id>/
Authentification : Oui (JWT ou session)
Paramètres :

Champ	Type	Obligatoire	Description
rating	int	Non	Nouvelle note (1-5)
comment	string	Non	Nouveau commentaire

Réponse :
200 OK avec la review mise à jour.

🗑️ Supprimer une review existante
URL : DELETE /api/community/reviews/<id>/
Authentification : Oui
Description : Supprime une review existante.
Réponse :
204 No Content

📄 Remarque sur les droits
Un utilisateur ne peut modifier ou supprimer que ses propres avis.

Les autres utilisateurs recevront un 403 Forbidden en cas de tentative.

📜 Pagination et filtrage (pour rappel)
Ajoute dans ton api_notes.md :

URL pour lister les reviews : GET /api/community/reviews/?activity_id=<id> ou ?event_id=<id>
Query Params optionnels :

Paramètre	Description
page	Numéro de page
page_size	Taille de page
min_rating	Filtrer par note minimale
max_rating	Filtrer par note maximale

Réponse :

json

{
  "count": 42,
  "next": "http://.../reviews/?activity_id=5&page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": { "id": 10, "username": "John" },
      "rating": 4,
      "comment": "Super activité !",
      "created_at": "2025-07-14T18:35:21Z"
    },
    ...
  ]
}


Auteur : Morice
Fichier : api_notes.md
Mis à jour le : 2025-07-15