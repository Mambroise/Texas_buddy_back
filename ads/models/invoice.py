# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/invoice.py
# Author : Morice
# ---------------------------------------------------------------------------

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from .advertisement import Advertisement
from ..services.invoice_reference import generate_invoice_reference


class AdInvoice(models.Model):
    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.CASCADE, related_name="invoices"
    )
    reference = models.CharField(max_length=50, unique=True, null=True, blank=True)
    period_start = models.DateField()
    period_end = models.DateField()
    period_impressions_count = models.PositiveIntegerField(default=0)
    period_clicks_count = models.PositiveIntegerField(default=0)
    period_conversions_count = models.PositiveIntegerField(default=0)
    generated_at = models.DateTimeField(auto_now_add=True)
    total_excluding_tax = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="USD")
    due_date = models.DateField()
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
        return f"Invoice {self.reference} - Advertisement {self.advertisement.title}"

    def clean(self):
        """
        Validate that the invoice period is within the advertisement's contract period.
        """
        if not self.advertisement:
            raise ValidationError("An invoice must be linked to an advertisement.")

        contract = self.advertisement.contract

        if not contract:
            raise ValidationError("The linked advertisement does not have an associated contract.")

        contract_start = contract.start_date
        contract_end = contract.end_date

        if self.period_start < contract_start:
            raise ValidationError(
                f"The invoice start date ({self.period_start}) cannot be before the contract start date ({contract_start})."
            )

        if self.period_end > contract_end:
            raise ValidationError(
                f"The invoice end date ({self.period_end}) cannot be after the contract end date ({contract_end})."
            )

        if self.period_start > self.period_end:
            raise ValidationError(
                "The invoice start date cannot be after the end date."
            )

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_invoice_reference()
        self.full_clean()  # Ensure validation always runs before saving
        super().save(*args, **kwargs)
