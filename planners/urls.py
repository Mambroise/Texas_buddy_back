# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :planners/urls.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.urls import path
from .views.trip_views import (
    TripListCreateView,
    TripDetailView,
)
from .views.tripday_views import (
    TripDayListCreateView,
    TripDayDetailView
)
from .views.tripstep_views import (
    TripDaySyncView,
    TripStepListCreateView,
    TripStepMoveView,
    TripStepDeleteView
)

app_name = 'planners'

urlpatterns = [
    path('trips/', TripListCreateView.as_view(), name='trip-list-create'),
    path('trips/<int:id>/', TripDetailView.as_view(), name='trip-detail'),
    path('trip-days/', TripDayListCreateView.as_view(), name='tripday-list-create'),
    path('trip-days/<int:pk>/sync/', TripDaySyncView.as_view(), name='tripday-sync'),
    path('trip-days/<int:id>/', TripDayDetailView.as_view(), name='tripday-detail'),
    path('trip-steps/', TripStepListCreateView.as_view(), name='tripstep-list-create'),
    path('trip-steps/<int:pk>/', TripStepDeleteView.as_view(), name='tripstep-delete'),
    path('trip-steps/<int:pk>/move/', TripStepMoveView.as_view(), name='tripstep-move'),
]

"""
Parfait. Voici l’exemple de la structure JSON attendue côté mobile lorsque l’utilisateur synchronise les TripStep d’un jour via :



POST /api/planners/trip-days/<trip_day_id>/sync/
✅ Exemple de payload envoyé depuis le mobile :
json

{
  "steps": [
    {
      "id": 21,
      "start_time": "09:00:00",
      "duration": 90,
      "activity_id": 5
    },
    {
      "id": 22,
      "start_time": "10:30:00",
      "duration": 60,
      "event_id": 12
    },
    {
      "id": 23,
      "start_time": "11:30:00",
      "duration": 45,
      "activity_id": 6
    }
  ]
}
🧠 Détails :
Champ	Type	Obligatoire	Description
id	int	✅	ID existant de la TripStep locale à mettre à jour
start_time	HH:MM:SS	✅	Heure de début (en UTC ou locale, à standardiser)
duration	int (minutes)	✅	Durée de l’étape
activity_id / event_id	int	✅	Soit activity_id, soit event_id, jamais les deux

🔄 Ce que fait le backend :
Identifie chaque TripStep par id.

Met à jour sa start_time, duration, et activity/event.

Ignore ou rejette toute step dont l’id ne correspond pas à un TripStep du TripDay concerné et appartenant à l’utilisateur connecté.


"""