# ---------------------------------------------------------------------------
#                            TEXAS BUDDY  ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/contract.py
# Author : Morice
# ---------------------------------------------------------------------------

from django.db import models
from.partner import Partner
from..services.contract_reference import generate_contract_reference # Assuming this generates a unique ref
from dateutil.relativedelta import relativedelta # Import moved here for clarity

class Contract(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="contracts", verbose_name="Partenaire")
    contract_reference = models.CharField(max_length=50, unique=True, verbose_name="Référence du Contrat/contract reference")
    
    # Dates du contrat principal
    start_date = models.DateField(verbose_name="Début du Contrat/Contract start_date")
    duration_months = models.PositiveIntegerField(verbose_name="Durée (en mois)/duration_months",)
    signed_date = models.DateField(verbose_name="Date de Signature/Signed_Date", help_text="Date à laquelle le contrat a été signé par les deux parties.")
    
    # Fichier du contrat signé (PDF)
    signed_contract_file = models.FileField(
        upload_to="contracts/signed_agreements/",
        blank=True,
        null=True,
        verbose_name="Fichier du Contrat Signé(PDF)/signed_contract_file(PDF)",
        help_text="Téléchargez le fichier PDF du contrat signé. Ce fichier doit être signé par les deux parties.",
    )

    # Termes généraux de tarification (le contrat cadre définit les principes, les IOs les détails)
    pricing_terms_description = models.TextField(
        blank=True,
        null=True,
        default="Rates specified in individual Insertion Orders(advertisements)",
        verbose_name="Description Générale des Termes de Tarification/pricing_terms_description",
        help_text="Décrit comment les tarifs sont déterminés pour les différents types de campagnes (ex: 'Tarifs spécifiés dans les Bons de Commande individuels')."
    )

    # Clauses légales importantes
    is_active = models.BooleanField(default=True, verbose_name="Contrat Actif")
    auto_renew = models.BooleanField(default=False, verbose_name="Renouvellement Automatique")
    renewal_period_months = models.PositiveIntegerField(
        null=True,blank=True,
        verbose_name="Période de Renouvellement(en mois)/renewal_period_months",
        help_text="Applicable si le renouvellement automatique est activé."
    )
    termination_date = models.DateField(
        null=True,blank=True,
        verbose_name="Date de Résiliation/termination_date"
    )
    termination_reason = models.TextField(
        blank=True,null=True,
        verbose_name="Raison de la Résiliation/termination_reason"
    )
    
    # Droit applicable et résolution des litiges
    GOVERNING_LAW_CHOICES = [
        ("TX", "Texas Law"),
        ("US_FEDERAL", "U.S. Federal Law"),
        ("OTHER", "Other (Specify in details)") # Option for future expansion if needed
    ]
    governing_law = models.CharField(
        max_length=10,
        choices=GOVERNING_LAW_CHOICES,
        default="TX",
        verbose_name="Droit Applicable/governing_law",
        help_text="Le droit applicable pour ce contrat. Par défaut, c'est le droit du Texas (Texas Law).",
    )
    
    DISPUTE_RESOLUTION_CHOICES = [
        ("NONE", "No dispute"),
        ("NEGOTIATION", "Negotiation"),
        ("MEDIATION", "Mediation"),
        ("ARBITRATION", "Arbitration"),
        ("LITIGATION", "Litigation (Court)"),
        ("MEDIATION_ARBITRATION", "Mediation then Arbitration") # Common combined approach
    ]
    dispute_resolution_method = models.CharField(
        max_length=25,
        choices=DISPUTE_RESOLUTION_CHOICES,
        default="NONE",
        verbose_name="Méthode Résolution des Litiges/dispute_resolution_method"
    )

    # Conformité TDPSA (Data Processing Agreement)
    data_processing_agreement_required = models.BooleanField(
        default=False,
        verbose_name="DPA Requis (TDPSA)/data_processing_agreement_required",
        help_text="Indique si un Accord de Traitement des Données est requis pour ce partenaire en vertu de la TDPSA."
    )
    data_processing_agreement_file = models.FileField(
        upload_to="contracts/dpa_agreements/",
        blank=True,null=True,
        verbose_name="Fichier DPA (TDPSA)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification/updated_at")

    @property
    def end_date(self):
        # Utilise relativedelta pour un calcul précis des dates
        return self.start_date + relativedelta(months=self.duration_months)

    def __str__(self):
        return f"Contrat {self.contract_reference} ({self.partner.name})"
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.contract_reference:
            self.contract_reference = generate_contract_reference()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Contrat Cadre/contract"
        verbose_name_plural = "Contrats Cadres"