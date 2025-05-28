# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from .views.user_endpoints import CustomerImportAPIView

app_name = 'users'

urlpatterns = [
    path('import-customer/', CustomerImportAPIView.as_view(), name='import-customer'),
]
