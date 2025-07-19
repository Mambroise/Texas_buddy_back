
# 🌟 Texas Buddy – Contexte Complet

## 🚀 Vision Générale
**Texas Buddy** est une application mobile de tourisme et de planification de voyages destinée :
- aux touristes **anglophones** (américains),
- aux touristes **francophones** (France, Belgique, Suisse, Canada…),
- aux touristes **hispanophones**,
- ainsi qu’aux **locaux** qui souhaitent redécouvrir leur État et profiter d’événements ou d’activités proches de chez eux.

Elle propose en temps réel des suggestions d’activités et d’événements autour de l’utilisateur, permet de planifier des itinéraires complets jour par jour, et intègre une dimension communautaire et un système de notifications.

Le back‑end est construit avec **Django REST Framework (DRF)** et une base de données **PostgreSQL**, tandis que le front‑end mobile est développé en **Flutter**.  
Hébergement prévu sur **AWS**.

---

## ⚙️ Modules et Architecture

### 🔑 Authentification
- **Modèle User** : basé sur `AbstractBaseUser` avec l’email comme identifiant principal.
- Enregistrement via un **code d’enregistrement** et un email.
- Authentification et gestion des sessions via **JWT** (access + refresh).
- Endpoints :
  - `POST /api/users/auth/login/` → obtient access/refresh tokens.
  - `POST /api/users/auth/token/refresh/` → rafraîchit le token.
- Logs d’événements d’authentification pour audit.

---

### 📍 Module Activités & Événements (`activities`)
- **Activity** : entités permanentes (musées, parcs, restaurants, lieux emblématiques…)
- **Event** : événements ponctuels (concerts, festivals, marchés saisonniers…)
- **Category** et **Promotion** pour classer et mettre en avant.
- Recherche par géolocalisation :
  - Paramètres `lat` et `lng` → tri croissant par distance.
  - Filtrage par catégorie, type, ou date.

---

### 🧭 Module Planification (`planners`)
- **Trip** : un voyage créé par l’utilisateur.
- **TripDay** : un jour spécifique dans un voyage.
- **TripStep** : une activité ou un événement ajouté à une journée avec un horaire.
- Fonctionnalités :
  - Drag-and-drop pour réordonner les TripStep.
  - Gestion automatique des chevauchements horaires.
  - Persistance temporaire SQLite côté mobile avant synchronisation API.
  - Suggestions dynamiques d’activités en fonction de la dernière étape.

---

### 🗺️ Carte en temps réel
- Affichage d’une **carte interactive** centrée sur la position actuelle du user.
- Les activités et événements proches apparaissent autour de lui.
- Possibilité de filtrer par type (restaurants, spectacles, nature, etc.).
- Interaction fluide avec le planificateur.

---

### 📢 Module Publicités (`ads`)
- Le système publicitaire a évolué :
  - **PriorityAd retiré.**
  - Remplacé par un **serveur publicitaire dynamique** qui sélectionne la meilleure publicité à chaque demande.
- Le serveur publicitaire prend en compte :
  - Format (interstitiel, native, push),
  - Proximité géographique,
  - Affinités de catégorie,
  - Contexte (heure, saison, événements en cours),
  - Consentement utilisateur.
- Résultats :
  - 1 seule pub pour un format interstitiel,
  - jusqu’à 3 pour le format native,
  - 1 pour le format push.
- Logs détaillés :
  - `AdImpression`, `AdClick`, `AdConversion` (avec champ JSON `details`).
- Exports disponibles en CSV, Excel stylisé multi‑onglets, et XML.

---

### 🔔 Module Notifications (`notifications`)
- Gestion centralisée des notifications dans l’application :
  - **Notifications push** : rappels d’événements, mise à jour de planning, suggestions d’activités.
  - **Messages in‑app** : conseils, alertes spéciales, annonces de partenaires.
  - **Emails** : confirmations, bilans de voyage, offres promotionnelles.
- Les notifications sont déclenchées par :
  - La planification d’un voyage,
  - La proximité d’un événement,
  - Une offre publicitaire ciblée,
  - Des actions communautaires (ex. quelqu’un commente ton itinéraire).

---

### 👥 Module Communauté (futur)
- Système de partage d’expériences entre voyageurs et locaux :
  - Commentaires sur des activités/événements,
  - Notation et recommandations,
  - Itinéraires publics consultables,
  - Possibilité de suivre d’autres utilisateurs.
- Objectif : créer une communauté active autour du tourisme au Texas.

---

## 🔧 Configuration Backend
- **Framework** : Django 4.x + Django REST Framework.
- **Auth** : `djangorestframework-simplejwt` (JWT).
- **DB** : PostgreSQL (production) + SQLite (cache mobile temporaire).
- **Hébergement** : AWS (Elastic Beanstalk ou EC2 + RDS).
- **Logs** : configuration avancée pour traçabilité des événements (auth, ads, planners…).
- **Export** : CSV, Excel (via `openpyxl`), XML (`xml.etree`).

---

## 🛠️ Fonctionnement futur (Workflow Utilisateur)

### 1️⃣ Accueil – Carte en temps réel
- Lancement → géolocalisation immédiate.
- Affichage d’activités et d’événements proches, filtrables.
- Publicités sélectionnées dynamiquement par le serveur publicitaire.

### 2️⃣ Découverte d’activités/événements
- Recherche par distance, type, catégorie.
- Accès aux détails complets et avis d’autres utilisateurs.

### 3️⃣ Planification de voyage
- Création d’un Trip (titre, dates),
- Ajout de TripDay et TripStep,
- Organisation des étapes par drag-and-drop,
- Sauvegarde et synchronisation côté serveur.

### 4️⃣ Notifications
- L’utilisateur reçoit des push pour des rappels, mises à jour ou suggestions pertinentes.
- Emails envoyés pour résumés et confirmations.

### 5️⃣ Communauté
- Partage d’itinéraires,
- Consultation et interaction avec les plans des autres,
- Système de suivi et de commentaires.

---

## 🔒 Sécurité & Authentification pour GPT Agents
- Utilisateur spécial `texasbuddy_gpt-agent@gpt.com` créé avec `is_staff=True`.
- Authentification via `/auth/login/` pour obtenir un **JWT Access**.
- Appels API sécurisés avec `Authorization: Bearer <token>`.

---

## ✅ Points Clés
- Public cible : touristes anglophones, francophones, hispanophones, et locaux.
- Modules majeurs : Users, Activities, Planners, Ads (serveur publicitaire), Notifications, Communauté.
- Backend DRF complet avec JWT, logs, exports multi-format.
- Frontend Flutter avec carte en temps réel, planificateur interactif.
- Orientation évolutive et ouverte à l’international.

---

**Auteur : Morice**  
*(Dernière mise à jour : Juillet 2025)*


