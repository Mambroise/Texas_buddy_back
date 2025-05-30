# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/views/registration_view.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from users.models.twofa import TwoFACode
from users.serializers import TwoFACodeVerificationSerializer

from ..models.user import User
from users.serializers import RegistrationVerificationSerializer
from ..service.twoFACode import generate_2fa_code

# Method first connexion to the app, checking the registration code sent to the customer
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class VerifyRegistrationAPIView(APIView):
    def post(self, request):
        serializer = RegistrationVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        registration_number = serializer.validated_data['registration_number']
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(registration_number=registration_number, email=email)
            generate_2fa_code(user)
            return Response({"detail": "Registration verified. Afa code sent"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid registration number or email."},
                status=status.HTTP_400_BAD_REQUEST
            )

# Method to check the 2 FA code sent after the registration code is valid on first connexion. Registration finalisation 
@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True), name='dispatch')
class Verify2FACodeAPIView(APIView):
    def post(self, request):
        serializer = TwoFACodeVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
            code_entry = TwoFACode.objects.filter(user=user, code=code, is_used=False).last()

            if not code_entry or code_entry.is_expired():
                return Response({"detail": "invalad code or expired."}, status=status.HTTP_400_BAD_REQUEST)

            # switch bool to true as code has been used
            code_entry.is_used = True
            code_entry.save()

            user.can_set_password = True
            user.save()

            return Response({"detail": "code valid. go to pwd creation"},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)
