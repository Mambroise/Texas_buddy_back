# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/contract_reference.py
# Author : Morice
# ---------------------------------------------------------------------------


import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

def generate_contract_reference():
    from ads.models import Contract  # local import to avoid circular imports

    year = timezone.now().year
    prefix = f"CTR-{year}-"
    logger.info("[ContractRef] Generating contract reference with prefix: %s", prefix)

    last = (
        Contract.objects
        .filter(contract_reference__startswith=prefix)
        .order_by('-contract_reference')
        .first()
    )

    if last:
        try:
            last_number = int(last.contract_reference.split('-')[-1])
            new_number = last_number + 1
            logger.info("[ContractRef] Last contract reference: %s → New number: %04d", last.contract_reference, new_number)
        except (IndexError, ValueError) as e:
            logger.error("[ContractRef] Failed to parse last contract number: %s (error: %s)", last.contract_reference, str(e))
            new_number = 1
    else:
        logger.info("[ContractRef] No existing contract found for prefix. Starting with 0001.")
        new_number = 1

    new_ref = f"{prefix}{str(new_number).zfill(4)}"
    logger.info("[ContractRef] Generated contract reference: %s", new_ref)
    return new_ref
