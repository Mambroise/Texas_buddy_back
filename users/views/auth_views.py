# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/views/auth_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from users.serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from users.models.twofa import TwoFACode
from users.serializers import TwoFACodeVerificationSerializer,SetPasswordSerializer,RegistrationVerificationSerializer,ResendRegistrationNumberSerializer
from ..models.user import User
from ..service.twoFACode import generate_2fa_code
from notifications.services.email_service import send_credentials_email

# Method first connexion to the app, checking the registration code sent to the customer
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class VerifyRegistrationAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistrationVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sign_up_number = serializer.validated_data['sign_up_number']
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(sign_up_number=sign_up_number, email=email)
            generate_2fa_code(user)
            return Response({"detail": "Registration verified. 2fa code sent"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid registration number or email."},
                status=status.HTTP_400_BAD_REQUEST
            )


# Method to check the 2 FA code sent after the registration code is valid on first connexion. Registration finalisation 
@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True), name='dispatch')
class Verify2FACodeAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = TwoFACodeVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
            code_entry = TwoFACode.objects.filter(user=user, code=code, is_used=False).last()

            if not code_entry or code_entry.is_expired():
                return Response({"detail": "invalid code or expired."}, status=status.HTTP_400_BAD_REQUEST)

            # switch bool to true as code has been used
            code_entry.is_used = True
            code_entry.save()

            user.can_set_password = True
            user.save()

            return Response({"detail": "code valid. You can now set your password"},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "No user found."}, status=status.HTTP_404_NOT_FOUND)

# Method to check the 2 FA code sent after the registration code is valid on first connexion. Registration finalisation 
@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True), name='dispatch')
class VerifyResetPwd2FACodeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = TwoFACodeVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
            code_entry = TwoFACode.objects.filter(user=user, code=code, is_used=False).last()

            if not code_entry or code_entry.is_expired():
                return Response({"detail": "invalid code or expired."}, status=status.HTTP_400_BAD_REQUEST)

            # switch bool to true as code has been used
            code_entry.is_used = True
            code_entry.save()

            user.can_set_password = True
            user.save()

            return Response({"detail": "code valid. You can now set your password"},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "No user found."}, status=status.HTTP_404_NOT_FOUND)


# Method to set the pwd in user entity
@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True), name='dispatch')
class SetPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)

            if not user.can_set_password:
                return Response({"detail": "Please, fulfill registration first."},
                                status=status.HTTP_403_FORBIDDEN)

            user.set_password(password)
            user.can_set_password = False
            user.is_active = True  # facultatif : si tu veux activer ici
            user.save()

            return Response({"detail": "Password succesfully set."},
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True), name='dispatch')
class ResendRegistrationNumberAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResendRegistrationNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            send_credentials_email(user)
            return Response({"detail": "Your Registration code has been sent by email."},
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "No user was found with your email."},
                            status=status.HTTP_404_NOT_FOUND)
        

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({"detail": "invalid Email or pssword."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"detail": "User not active yet."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    
    
# logged in User ask for a password reset 
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class RequestPasswordResetAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            generate_2fa_code(user)
            return Response({"detail": "Security code has been sent by email."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "No user with this email was found ."}, status=status.HTTP_404_NOT_FOUND)

    
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
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


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
  "detail": "Déconnexion de tous les appareils réussie."
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
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class LogoutAllAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        tokens = OutstandingToken.objects.filter(user=user)

        for token in tokens:
            try:
                # Blackliste le token s'il ne l'est pas déjà
                BlacklistedToken.objects.get_or_create(token=token)
            except Exception as e:
                continue

        return Response({"detail": "All devices logged out."}, status=status.HTTP_200_OK)
