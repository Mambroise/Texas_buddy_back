# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/invoice.py
# Author : Morice
# ---------------------------------------------------------------------------

from django.db import models
from django.conf import settings
from .partner import Partner


class AdInvoice(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    
    reference = models.CharField(max_length=50, unique=True, null=True, blank=True)
    period_start = models.DateField()
    period_end = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="USD")
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ("wire_transfer", "Wire Transfer"),
            ("credit_card", "Credit Card"),
            ("check", "Check"),
            ("paypal", "PayPal"),
        ],
    )
    notes = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to="invoices/", blank=True, null=True)

    def __str__(self):
        return f"Invoice {self.reference} - Partner {self.partner.name}"
