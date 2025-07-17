# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : ads/views/review_service.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.core.exceptions import ValidationError
from activities.models import Activity, Event
from community.models import Review
import logging

logger = logging.getLogger(__name__)

class ReviewService:
    @staticmethod
    def can_review(user, target):
        # TODO: Remplacer par une vraie logique de vérification (ex: vérifier un modèle Visit)
        # Pour l'instant on autorise tout :
        return True

    @classmethod
    def create_review(cls, user, target_type, target_id, rating, comment=None):
        if target_type == 'activity':
            target = Activity.objects.get(id=target_id)
        else:
            target = Event.objects.get(id=target_id)

        if not cls.can_review(user, target):
            raise ValidationError("You cannot review unvisited spots.")

        review = Review.objects.create(
            user=user,
            activity=target if target_type == 'activity' else None,
            event=target if target_type == 'event' else None,
            rating=rating,
            comment=comment or ""
        )
        logger.info(f"Review created by user {user.id} for {target_type}={target_id} with rating={rating}")
        return review
