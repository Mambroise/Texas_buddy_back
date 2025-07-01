# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :users/views/auth_views.py
# Author : Morice
# ---------------------------------------------------------------------------


import logging
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from users.serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.utils.translation import gettext as _
from core.throttles import PostRateLimitedAPIView

from users.models.twofa import TwoFACode
from users.serializers import (TwoFACodeVerificationSerializer,
                               SetPasswordSerializer,
                               RegistrationVerificationSerializer,
                               ResendRegistrationNumberSerializer)
from ..models.user import User
from ..service.twoFACode import generate_2fa_code
from notifications.services.email_service import send_credentials_email

# ─── Logger Setup ──────────────────────────────────────────────────────────
logger = logging.getLogger('texasbuddy')

# ─── View: VerifyRegistrationAPIView ───────────────────────────────────────────
# Method first connexion to the app, checking the registration code sent to the customer
class VerifyRegistrationAPIView(PostRateLimitedAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class   

    def post(self, request):
        logger.info("Incoming sign_up_number verification request: %s", request.data)
        serializer = RegistrationVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sign_up_number = serializer.validated_data['sign_up_number']
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(sign_up_number=sign_up_number, email=email)

            if user.is_active:
                logger.warning(f"[VERIFY_REGISTRATION] Account already active: {email}")
                return Response(
                    {"detail": _("This account is already active. Please log in instead.")},
                    status=status.HTTP_400_BAD_REQUEST
                )

            generate_2fa_code(user)
            return Response({"message": _("Registration verified. 2fa code sent")}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            logger.error("[VERIFY_REGISTRATION] sign_up_number verification failed: user not found for email %s", email)
            return Response(
                {"detail": _("Invalid registration number or email.")},
                status=status.HTTP_400_BAD_REQUEST
            )


# Method to check the 2 FA code sent after the registration code is valid on first connexion. Registration finalisation 
class Verify2FACodeAPIView(PostRateLimitedAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def post(self, request):
        logger.info("[2FA_REGISTRATION] Incoming 2FACode verification request: %s", request.data)
        serializer = TwoFACodeVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
            code_entry = TwoFACode.objects.filter(user=user, code=code, is_used=False).last()
            if not code_entry or code_entry.is_expired():
                logger.warning("[2FA_REGISTRATION] expired or missing request: %s", request.data)
                return Response({"detail": _("invalid code or expired.")}, status=status.HTTP_400_BAD_REQUEST)

            # switch bool to true as code has been used
            code_entry.is_used = True
            code_entry.save()

            user.can_set_password = True
            user.save()
            logger.info("[2FA_REGISTRATION] 2FACode verification successful for user: %s", email)

            return Response({"message": _("code valid. You can now set your password")},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error("[2FA_REGISTRATION] 2FA verification failed: user not found for email %s", email)
            return Response({"detail": _("No user found.")}, status=status.HTTP_404_NOT_FOUND)

# Method to check the 2 FA code sent after the registration code is valid on first connexion. Registration finalisation 
class VerifyResetPwd2FACodeAPIView(PostRateLimitedAPIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def post(self, request):
        logger.info("[2FA_RESET_PWD] Incoming 2FACode verification for user: %s", request.user.email)
        serializer = TwoFACodeVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
            code_entry = TwoFACode.objects.filter(user=user, code=code, is_used=False).last()

            if not code_entry or code_entry.is_expired():
                logger.warning("[2FA_REGISTRATION] expired or missing request: %s", request.data)
                return Response({"detail": _("invalid code or expired.")}, status=status.HTTP_400_BAD_REQUEST)

            # switch bool to true as code has been used
            code_entry.is_used = True
            code_entry.save()
            logger.info("[2FA_RESET_PWD] 2FACode verification successful for user: %s", email)

            user.can_set_password = True
            user.save()

            return Response({"message": _("code valid. You can now set your password")},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error("[2FA_RESET_PWD] 2FA verification failed: user not found for email %s", email)
            return Response({"detail": _("No user found.")}, status=status.HTTP_404_NOT_FOUND)


# Method to set the pwd in user entity
class SetPasswordAPIView(PostRateLimitedAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class
    def get_client_ip(self, request):
        """Récupère l’adresse IP réelle même derrière un proxy."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        logger.info("[RESET_PASSWORD] Incoming pwd data for user: %s", request.user.email)
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)

            if not user.can_set_password:
                logger.warning(f"[RESET_PASSWORD] Attempt to reset without verification: {email}")
                return Response({"detail": _("Please, fulfill registration first.")},
                                status=status.HTTP_403_FORBIDDEN)

            user.set_password(password)
            user.can_set_password = False
            user.is_active = True  
            user.save()
            logger.info(f"[RESET_PASSWORD] Password successfully set for: {email}")
            
            # Save the IP if user is active
            if user.is_active and not user.first_ip:
                    user.first_ip = self.get_client_ip(request)
                    user.save(update_fields=["first_ip"])
                    logger.info(f"[RESET_PASSWORD] First IP saved for: {email}")


            return Response({"message": _("Password succesfully set.")},
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error("[RESET_PASSWORD] Password set failed: user not found for email %s", email)
            return Response({"detail": _("User not found.")}, status=status.HTTP_404_NOT_FOUND)


class ResendRegistrationNumberAPIView(PostRateLimitedAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def post(self, request):
        logger.info("[RESEND_SIGN_UP_NUMBER] Incoming data for user: %s", request.user.email)
        serializer = ResendRegistrationNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            send_credentials_email(user)
            logger.info("[RESEND_SIGN_UP_NUMBER] sign_up_number successfully sent by email to user: %s", request.user.email)

            return Response({"message": _("Your Registration code has been sent by email.")},
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error("[RESEND_SIGN_UP_NUMBER] Sign_up_number could not be sent: user not found for email %s", email)
            return Response({"detail": _("No user was found with your email.")},
                            status=status.HTTP_404_NOT_FOUND)
        

class LoginAPIView(PostRateLimitedAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        logger.info("[LOGIN] Incoming login data for user: %s", email)

        user = authenticate(request, username=email, password=password)

        if user is None:
            logger.warning(f"[LOGIN] Failed login attempt for: {email}")
            return Response({"detail": _("invalid Email or pssword.")}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            logger.warning(f"[LOGIN] Inactive user login attempt: {email}")
            return Response({"detail": _("User not active yet.")}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        logger.info(f"[LOGIN] Login successful for: {email}")

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    
    
# logged in User ask for a password reset 
class RequestPasswordResetAPIView(PostRateLimitedAPIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def post(self, request):
        logger.info("[REQUEST_PASSWORD_RESET] Incoming data for user: %s", request.user.email)
        email = request.data.get("email")
        if not email:
            logger.warning("[REQUEST_PASSWORD_RESET] Missing email in request.")
            return Response({"detail": _("Email is required.")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            generate_2fa_code(user)
            logger.info("[REQUEST_PASSWORD_RESET] 2FA code successfully sent to user: %s", request.user.email)
            return Response({"message": _("Security code has been sent by email.")}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error("[REQUEST_PASSWORD_RESET] Password reset failed: user not found for email %s", email)
            return Response({"detail": _("No user with this email was found.")}, status=status.HTTP_404_NOT_FOUND)

    
# logout standard, pour déconnecter un appareil de l'application
""" 
🔁 3. Comment utiliser ces tokens
✅ Pour faire une requête à un endpoint protégé
Tu dois inclure le access token dans les headers :

bash

POST /api/mes-données/
Authorization: Bearer <access_token>

🔁 Pour rafraîchir ton access token quand il expire
Tu envoies seulement le refresh token :

swift
POST /api/token/refresh/
{
  "refresh": "<refresh_token>"
}
Et tu reçois un nouveau access token.

🚪 Pour se déconnecter (logout)
Tu dois :

Fournir le refresh token dans le body JSON

Fournir le access token dans les headers pour t’authentifier

✅ Exemple complet :
URL : /api/logout/
Méthode : POST
Headers :

http
Authorization: Bearer <access_token

Body JSON :
json
{
  "refresh": "<refresh_token>"
}

🔐 Cela indique : "Je suis connecté (avec le access token), et je veux invalider mon refresh token pour empêcher toute reconnection."
🔓 1. Logout standard (LogoutAPIView avec token refresh)
✅ Cas d’usage :
Un utilisateur se déconnecte volontairement depuis un appareil (ex. son téléphone).

Il quitte une session sans affecter ses autres connexions (par exemple, connecté aussi sur une tablette).

💡 Exemple :
Morice utilise l'app sur son smartphone et sa tablette. Il quitte l'app sur le smartphone → on appelle /logout/ avec le token refresh de cette session uniquement.


"""
class LogoutAPIView(PostRateLimitedAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"[LOGOUT] User {request.user.email} logged out successfully.")
            return Response({"message": _("Logout successful.")}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.warning(f"[LOGOUT] Logout failed for user {request.user.email}: {str(e)}")
            return Response({"detail": _("Invalid or expired token.")}, status=status.HTTP_400_BAD_REQUEST)

""" 
📬 3. Exemple d’appel Postman
URL : POST /api/logout-all/
Headers :

http
Authorization: Bearer <access_token>
Body : (vide)

Réponse :

json
{
  "message": "Déconnexion de tous les appareils réussie."
}

🚪 2. Logout global (LogoutAllAPIView sans besoin de token refresh)
✅ Cas d’usage :
L’utilisateur pense que quelqu’un d’autre est connecté à son compte.

Il souhaite forcer la déconnexion sur tous les appareils.

Par exemple, après avoir changé son mot de passe.

💡 Exemple :
Morice remarque une activité suspecte sur son compte. Depuis la page “Sécurité”,
 il appuie sur “Se déconnecter partout” → appel à /logout_all/ → tous les tokens sont invalidés.
"""
class LogoutAllAPIView(PostRateLimitedAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = []  # Disable throttling for this view, as it's already rate-limited by the base class

    def post(self, request):
        user = request.user
        tokens = OutstandingToken.objects.filter(user=user)

        blacklisted_count = 0
        for token in tokens:
            try:
                _, created = BlacklistedToken.objects.get_or_create(token=token)
                if created:
                    blacklisted_count += 1
            except Exception as e:
                logger.error(f"[LOGOUT_ALL] Error blacklisting token for user {user.email}: {str(e)}")
                continue

        logger.info(f"[LOGOUT_ALL] {user.email} logged out from all devices. {blacklisted_count} tokens blacklisted.")
        