# ---------------------------------------------------------------------------
# 📌 TEXAS BUDDY – API Notes (2025)
# ---------------------------------------------------------------------------

## 🔑 Authentification & Gestion Utilisateur
📌 API Notes – Users (2025)
Toutes ces routes utilisent les sérializers et throttles personnalisés.
👉 Important : toujours inclure la langue souhaitée dans le header via X-Language ou Accept-Language pour activer la traduction dynamique des messages.

=====================================================
🔹 1. POST /api/users/import-customer/
Vue : CustomerImportAPIView
Accès : Public (pas besoin d’être authentifié)
Rôle : Créer un utilisateur depuis une source externe (import d’un client).

Headers attendus :

yaml

X-Language: fr      # ou en, es, etc.
Content-Type: application/json
Body attendu :

json

{
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "1245789632",
  "address": "56 MyAddress",
  "country": "France",
  "sign_up_number": "245366548"
}
Réponse succès :

json

{
  "success": true,
  "message": "User created"
}
Réponse erreur :

json

{
  "success": false,
  "errors": {
    "email": ["This field is required."]
  }
}


---

===================================================
### ✅ `POST /auth/verify-registration/`
**View:** `VerifyRegistrationAPIView`  
**But :**  
Vérifier le **numéro d’enregistrement (sign_up_number)** envoyé à un client lors de sa première connexion.

Headers attendus :

yaml

X-Language: fr      # ou en, es, etc.
Content-Type: application/json
**Payload attendu :**
```json
{
  "email": "user@example.com",
  "sign_up_number": "ABCD1234"
}

===================================================
✅ POST /auth/resend-registration-number/
View: ResendRegistrationNumberAPIView
But :
Renvoyer le sign_up_number par email au client.
Headers attendus :

yaml

X-Language: fr      # ou en, es, etc.
Content-Type: application/json

Payload attendu :

json

{
  "email": "user@example.com"
}
Réponses :

200 OK : {"message": "Your Registration code has been sent by email."}

404 NOT FOUND : email inconnu

==================================================
🔹 2. GET & PATCH /api/users/users/me/
Vue : UserProfileView
Accès : Authentifié (Bearer Token requis)
Rôle :

GET : récupérer son profil utilisateur.

PATCH : modifier partiellement son profil (ex. prénom, nom).

Headers attendus :

pgsql

Authorization: Bearer <token>
X-Language: fr
Content-Type: application/json
Exemple PATCH Body :

json

{
  "first_name": "Jean",
  "last_name": "Dupont"
}
Réponse GET exemple :

json

{
  "id": 1,
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "MySecret123",
  "address": "MySecret123",
  "country": "France",
  "interests": [3, 5]
}

====================================================
🔹 3. POST /api/users/password-reset/confirm/
Vue : ConfirmPasswordResetAPIView
Accès : Public (pas besoin d’être authentifié)
Rôle : Changer le mot de passe d’un utilisateur autorisé à le faire (can_set_password = True).

Headers attendus :

pgsql

X-Language: fr
Content-Type: application/json
Body attendu :

json

{
  "email": "john@example.com",
  "password": "NewStrongPassword!"
}
Réponse succès :

json

{
  "message": "password successfully reset."
}
Réponse erreur :

json

{
  "detail": "reset not authorized."
}

=====================================================
🔹 4. PATCH /api/users/me/interests/
Vue : UpdateUserInterestsView
Accès : Authentifié
Rôle : Modifier les centres d’intérêt liés à un utilisateur.

Headers attendus :

pgsql

Authorization: Bearer <token>
X-Language: fr
Content-Type: application/json
Body attendu :

json

{
  "interests": [1, 4, 7]
}
Réponse succès :

json

{
  "id": 1,
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "interests": [1, 4, 7]
}
✅ ⚡ Notes importantes :

Tous les messages (User created, password successfully reset, etc.) sont traduits en fonction de la langue passée dans le header.

Si aucun header X-Language ou Accept-Language n’est envoyé, la langue par défaut du projet sera utilisée.

Les routes sont protégées par un système de throttling (ex. max 8 GET/min pour le profil, etc.).

