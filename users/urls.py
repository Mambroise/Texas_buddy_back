# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views.user_views import CustomerImportAPIView,UserProfileView,ConfirmPasswordResetAPIView
from users.views.auth_views import VerifyRegistrationAPIView, Verify2FACodeAPIView,SetPasswordAPIView,ResendRegistrationNumberAPIView,LoginAPIView,LogoutAPIView,LogoutAllAPIView,RequestPasswordResetAPIView,VerifyResetPwd2FACodeAPIView

app_name = 'users'

urlpatterns = [
    path('import-customer/', CustomerImportAPIView.as_view(), name='import-customer'),
    path("auth/resend-registration-number/", ResendRegistrationNumberAPIView.as_view(), name="resend-registration"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/verify-registration/", VerifyRegistrationAPIView.as_view(), name="veriUserProfileViewfy-registration"),
    path("auth/verify-2fa-code/", Verify2FACodeAPIView.as_view(), name="verify-2fa"),
    path("auth/verify-restpwd-2fa-code/", VerifyResetPwd2FACodeAPIView.as_view(), name="verify-2fa"),
    path("auth/set-password/", SetPasswordAPIView.as_view(), name="set-password"),
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
    path('password-reset/request/', RequestPasswordResetAPIView.as_view()),
    path('password-reset/verify-code/', VerifyResetPwd2FACodeAPIView.as_view()),
    path('password-reset/confirm/', ConfirmPasswordResetAPIView.as_view()),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path('logout-all/', LogoutAllAPIView.as_view(), name='logout_all'),

    #  Important!! url qui rafraichit le token access pour éviter l'expiration 
    #  Le refresh sera effectué par un middlware dans flutter qui l'effectuera tant qu'il y aura de l'activité sur l'appli
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
