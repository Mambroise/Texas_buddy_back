# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/partner.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models

# Create your models here.
class Partner(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    contract_signed_date = models.DateField(null=True, blank=True)
    contract_type = models.CharField(max_length=20, choices=[
        ("CPM", "CPM"),
        ("CPC", "CPC"),
        ("CPA", "CPA"),
        ("FORFAIT", "Forfait"),
        ("PACK", "Pack Premium"),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)