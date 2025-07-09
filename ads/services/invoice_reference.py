# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/invoice_reference.py
# Author : Morice
# ---------------------------------------------------------------------------

import logging
from django.utils import timezone
from django.db.models import Max

logger = logging.getLogger(__name__)


def generate_invoice_reference():
    from ads.models import AdInvoice  # import local pour éviter circular imports

    year = timezone.now().year
    prefix = f"INV-{year}-"

    logger.debug("[InvoiceReference] Generating invoice reference with prefix '%s'", prefix)

    try:
        max_ref = (
            AdInvoice.objects
            .filter(reference__startswith=prefix)
            .aggregate(max_num=Max("reference"))
        )
        last_ref = max_ref["max_num"]

        if last_ref:
            last_number = int(last_ref.split("-")[-1])
            new_number = last_number + 1
            logger.debug("[InvoiceReference] Last invoice ref: %s → New number: %04d", last_ref, new_number)
        else:
            new_number = 1
            logger.debug("[InvoiceReference] No previous invoice found. Starting at 0001.")

        new_ref = f"{prefix}{new_number:04d}"
        logger.info("[InvoiceReference] New invoice reference generated: %s", new_ref)
        return new_ref

    except Exception as e:
        logger.error("[InvoiceReference] Failed to generate invoice reference: %s", str(e), exc_info=True)
        raise
