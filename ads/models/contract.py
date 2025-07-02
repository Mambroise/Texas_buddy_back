# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/contract.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from .partner import Partner
from ..services.contract_reference import generate_contract_reference

class Contract(models.Model):
    CAMPAIGN_TYPE_CHOICES = [
        ("CPM", "CPM"),
        ("CPC", "CPC"),
        ("CPA", "CPA"),
        ("FORFAIT", "Forfait"),
        ("PACK", "Pack Premium"),
    ]

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="contracts")
    contract_reference = models.CharField(max_length=50, unique=True)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES)
    start_date = models.DateField()
    duration_months = models.PositiveIntegerField()
    signed_date = models.DateField()
    cpm_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    cpc_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    cpa_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    forfait_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def end_date(self):
        from dateutil.relativedelta import relativedelta
        return self.start_date + relativedelta(months=self.duration_months)

    def __str__(self):
        return f"{self.contract_reference} ({self.partner.name})"
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.contract_reference:
            self.contract_reference = generate_contract_reference()
        super().save(*args, **kwargs)

