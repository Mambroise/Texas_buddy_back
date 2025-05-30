# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from .views.user_views import CustomerImportAPIView
from users.views.auth_views import VerifyRegistrationAPIView, Verify2FACodeAPIView

app_name = 'users'

urlpatterns = [
    path('import-customer/', CustomerImportAPIView.as_view(), name='import-customer'),
    path("auth/verify-registration/", VerifyRegistrationAPIView.as_view(), name="verify-registration"),
    path("auth/verify-2fa-code/", Verify2FACodeAPIView.as_view(), name="verify-2fa"),
]
