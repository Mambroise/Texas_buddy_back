# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/contract_reference.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.utils import timezone

def generate_contract_reference():
    from ads.models import Contract  # import local pour éviter circular imports
    year = timezone.now().year
    prefix = f"CTR-{year}-"
    last = (
        Contract.objects
        .filter(contract_reference__startswith=prefix)
        .order_by('-contract_reference')
        .first()
    )
    if last:
        last_number = int(last.contract_reference.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1
    return f"{prefix}{str(new_number).zfill(4)}"
