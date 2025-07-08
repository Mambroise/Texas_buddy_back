# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/partner.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models

class Partner(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    legal_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField()
    address = models.CharField(blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True, default="TEXAS") 
    country = models.CharField(max_length=100, blank=True,default="USA")
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    tax_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="EIN/Tax ID(Numéro d'identification fiscale)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes Internes / Internal Partner Notes",
        help_text="Informations supplémentaires ou historiques sur ce partenaire."
    )

    class Meta:
        verbose_name = "Partenaire/partner"
        verbose_name_plural = "Partenaires/partners"
        
    def __str__(self):
        return self.legal_name
