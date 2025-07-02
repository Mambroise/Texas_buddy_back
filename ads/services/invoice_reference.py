# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/invoice_reference.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.utils import timezone
from django.db.models import Max

def generate_invoice_reference():
    from ads.models import AdInvoice
    """
    Generates a unique invoice reference in the format:
    INV-YYYY-XXXX
    """
    year = timezone.now().year

    # Find the highest existing number for this year
    max_ref = (
        AdInvoice.objects
        .filter(reference__startswith=f"INV-{year}-")
        .aggregate(max_num=Max("reference"))
    )

    last_ref = max_ref["max_num"]

    if last_ref:
        # Extract the numeric part and increment
        last_number = int(last_ref.split("-")[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"INV-{year}-{new_number:04d}"
