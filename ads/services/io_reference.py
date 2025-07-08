# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/views/io_reference.py
# Author : Morice
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
#                           TEXAS BUDDY  ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/services/io_reference.py
# Author : Morice
# ---------------------------------------------------------------------------

from django.utils import timezone
from django.db.models import Max

def generate_io_reference():
    # We need to import the Advertisement model here to avoid circular imports
    # if Advertisement also imports from this service.
    # It's generally better to pass the model as an argument or ensure
    # the import happens within the function if strictly necessary.
    # For simplicity, we'll import it here, assuming `Advertisement`
    # doesn't directly import `generate_io_reference` at the module level
    # (only in the save method, which is fine).
    from ads.models import Advertisement 

    """
    Generates a unique IO (Insertion Order) reference in the format:
    IO-YYYY-XXXX
    """
    year = timezone.now().year

    # Find the highest existing IO number for this year
    # We filter by 'io_reference_number' which is the field for the IO reference.
    max_io_ref = (
        Advertisement.objects
        .filter(io_reference_number__startswith=f"IO-{year}-")
        .aggregate(max_num=Max("io_reference_number"))
    )

    last_io_ref = max_io_ref["max_num"]

    if last_io_ref:
        # Extract the numeric part and increment
        last_number = int(last_io_ref.split("-")[-1])
        new_number = last_number + 1
    else:
        # If no existing IOs for the current year, start from 1
        new_number = 1

    return f"IO-{year}-{new_number:04d}"