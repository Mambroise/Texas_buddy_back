# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :users/views/user_views.py
# Author : Morice
# ---------------------------------------------------------------------------

import logging
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status,permissions
from rest_framework.generics import RetrieveUpdateAPIView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.utils.translation import gettext as _

from ..serializers import UserSerializer,SetPasswordSerializer,UserInterestsUpdateSerializer
from ..models import User
from core.throttles import PostRateLimitedAPIView,PatchRateLimitedAPIView

# ─── Logger Setup ──────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ─── View: CustomerImportAPIView ───────────────────────────────────────────

class CustomerImportAPIView(PostRateLimitedAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("Incoming user registration request: %s", request.data)

        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                logger.info("User successfully created: %s", user.email)
                return Response({"success": True, "message": _("User created")}, status=status.HTTP_201_CREATED)
            else:
                logger.warning("[USER_IMPORT] User creation failed due to validation errors: %s", serializer.errors)
        except Exception as e:
            logger.exception(f"[USER_IMPORT] Unexpected exception during user creation : {e}")

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ratelimit(key='ip', rate='8/m', method='GET', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True), name='dispatch')
class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        logger.info("User profile accessed: %s", self.request.user.email)
        return self.request.user

    def patch(self, request, *args, **kwargs):
        logger.info("User profile update request from: %s", request.user.email)
        return super().patch(request, *args, **kwargs)

class ConfirmPasswordResetAPIView(PostRateLimitedAPIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        logger.info("Password reset data received for: %s", request.data.get("email"))

        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)

            if not user.can_set_password:
                logger.warning("[REST_PASSWORD] Password reset denied for %s: can_set_password is False", email)
                return Response({"detail": _("reset not authorized.")}, status=status.HTTP_403_FORBIDDEN)

            user.set_password(password)
            user.can_set_password = False
            user.save()

            logger.info("Password successfully reset for user: %s", email)
            return Response({"message": _("password successfully reset.")}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error("[REST_PASSWORD] Password reset failed: user not found for email %s", email)
            return Response({"detail": _("User not found.")}, status=status.HTTP_404_NOT_FOUND)



class UpdateUserInterestsView(PatchRateLimitedAPIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user_email = request.user.email
        logger.info("[INTERESTS_UPDATE] Update interests request from user: %s | Payload: %s", user_email, request.data)

        try:
            serializer = UserInterestsUpdateSerializer(
                instance=request.user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                logger.info("[INTERESTS_UPDATE] Interests successfully updated for user: %s | New interests IDs: %s",
                            user_email,
                            request.data.get('interests'))
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.warning("[INTERESTS_UPDATE] Validation failed for user: %s | Errors: %s",
                               user_email,
                               serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("[INTERESTS_UPDATE] Unexpected exception for user %s: %s", user_email, e)
            return Response({"detail": _("An unexpected error occurred.")},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)