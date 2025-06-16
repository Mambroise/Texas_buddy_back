# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :activities/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from .views.activity_views import ActivityListAPIView,ActivityDetailAPIView
from .views.event_views import EventListAPIView,EventDetailAPIView
from .views.category_views import CategoryListAPIView

app_name = 'activities'
urlpatterns = [
    path("activities/", ActivityListAPIView.as_view(), name="activity-list"),
    path("activities/<int:id>/", ActivityDetailAPIView.as_view(), name='activity-detail'),
    path("events/", EventListAPIView.as_view(), name="event-list"),
    path("events/<int:id>/", EventDetailAPIView.as_view(), name="event-detail"),
    path("categories/", CategoryListAPIView.as_view(), name="category-list"),
 ]

"""
1. 🔍 Lister toutes les activités (en temps réel)

GET /api/activities/
– Utilise timezone.now() comme date de référence.
– Renvoie toutes les activités, et celles avec une promotion actuelle auront has_promotion: true.

2. 📅 Lister les activités à une date spécifique (planificateur de voyage)

GET /api/activities/?date=2025-07-15
– Renvoie toutes les activités, mais has_promotion: true uniquement si une promo est active à cette date-là.

3. 🗂️ Filtrer par catégorie

GET /api/activities/?category=Musée,Parc
4. 🔍 Recherche par nom ou ville

GET /api/activities/?search=dallas
5. 📊 Trier les résultats (ex: par prix croissant)

GET /api/activities/?ordering=price
6. 💡 Combinaison possible

GET /api/activities/?category=Musée&date=2025-08-10&ordering=price&search=houston"""