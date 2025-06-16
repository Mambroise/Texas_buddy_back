# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/config/urls.py
# Author : Morice
# ---------------------------------------------------------------------------

from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView,SpectacularRedocView
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # Swagger, Redoc, etc.
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # apps routes
    path('api/users/', include('users.urls', namespace='users')),
    path('api/activities/', include('activities.urls', namespace='activities')),
    path('api/planners/', include('planners.urls', namespace='planners')),
    path('api/ads/', include('ads.urls', namespace='ads')),
    path('api/community/', include('community.urls', namespace='community')),
    path('api/core/', include('core.urls', namespace='core')),
    path('api/notifications/', include('notifications.urls', namespace='notifications')),
    
]
# Ajout du support des langues
urlpatterns = i18n_patterns(*urlpatterns)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

