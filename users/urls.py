# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from .views.user_views import CustomerImportAPIView
from users.views.auth_views import VerifyRegistrationAPIView, Verify2FACodeAPIView,SetPasswordAPIView,ResendRegistrationNumberAPIView,LoginAPIView,LogoutAPIView,LogoutAllAPIView

app_name = 'users'

urlpatterns = [
    path('import-customer/', CustomerImportAPIView.as_view(), name='import-customer'),
    path("auth/resend-registration-number/", ResendRegistrationNumberAPIView.as_view(), name="resend-registration"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/verify-registration/", VerifyRegistrationAPIView.as_view(), name="verify-registration"),
    path("auth/verify-2fa-code/", Verify2FACodeAPIView.as_view(), name="verify-2fa"),
    path("auth/set-password/", SetPasswordAPIView.as_view(), name="set-password"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path('logout-all/', LogoutAllAPIView.as_view(), name='logout_all'),
]
