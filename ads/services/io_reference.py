# ---------------------------------------------------------------------------
#                           TEXAS BUDDY  ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/services/io_reference.py
# Author : Morice
# ---------------------------------------------------------------------------

from django.utils import timezone
from django.db.models import Max
import logging

logger = logging.getLogger(__name__)


def generate_io_reference():
    """
    Génère une référence IO (Insertion Order) unique au format :
    IO-YYYY-XXXX
    """
    from ads.models import Advertisement  # Import local pour éviter les imports circulaires

    try:
        year = timezone.now().year
        logger.debug("[IOReference] Generating IO reference for year %d", year)

        # Cherche la dernière référence existante de l’année
        max_io_ref = (
            Advertisement.objects
            .filter(io_reference_number__startswith=f"IO-{year}-")
            .aggregate(max_num=Max("io_reference_number"))
        )

        last_io_ref = max_io_ref["max_num"]
        logger.debug("[IOReference] Last IO reference found: %s", last_io_ref)

        if last_io_ref:
            # Extrait la partie numérique et incrémente
            last_number = int(last_io_ref.split("-")[-1])
            new_number = last_number + 1
        else:
            # Aucune référence encore enregistrée cette année
            new_number = 1

        new_io_ref = f"IO-{year}-{new_number:04d}"
        logger.info("[IOReference] New IO reference generated: %s", new_io_ref)
        return new_io_ref

    except Exception as e:
        logger.error("[IOReference] Error generating IO reference: %s", str(e), exc_info=True)
        raise
