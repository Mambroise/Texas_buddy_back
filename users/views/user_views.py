# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/views/user_views.py
# Author : Morice
# ---------------------------------------------------------------------------


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from rest_framework.generics import RetrieveUpdateAPIView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from ..serializers import UserSerializer,SetPasswordSerializer
from ..models import User

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class CustomerImportAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({"success": True, "message": "User created"}, status=status.HTTP_201_CREATED)
            else:
                print("serializer errors:", serializer.errors)
        except Exception as e:
            import traceback
            traceback.print_exc()  
            print(f"exception user: {e}")

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class ConfirmPasswordResetAPIView(APIView):
    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)

            if not user.can_set_password:
                return Response({"detail": "Réinitialisation non autorisée."}, status=status.HTTP_403_FORBIDDEN)

            user.set_password(password)
            user.can_set_password = False
            user.save()

            return Response({"detail": "Mot de passe réinitialisé avec succès."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)
