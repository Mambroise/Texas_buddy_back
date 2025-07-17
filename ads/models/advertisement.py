# ---------------------------------------------------------------------------
#                            TEXAS BUDDY  ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/models/advertisement.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from django.core.exceptions import ValidationError

from .contract import Contract
from activities.models import Activity, Event 
from ..services.io_reference import generate_io_reference 

class Advertisement(models.Model):
    # Identifiant unique pour chaque Bon de Commande (IO)
    io_reference_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Référence commande/io_reference_number",
    )
    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="advertisements",
        verbose_name="Contrat Cadre/contract"
    )

    # Types de campagne (déplacés ici car spécifiques à l'IO)
    CAMPAIGN_TYPE_CHOICES = [
        ("CPM", "CPM"),
        ("CPC", "CPC"),
        ("CPA", "CPA"),
        ("COMBO", "Combo"),
        ("PACKAGE", "Package"),
        ("PREMIUM", "Pack Premium"),
    ]
    campaign_type = models.CharField(
        max_length=20,
        choices=CAMPAIGN_TYPE_CHOICES,
        default="COMBO",
        verbose_name="Type de Campagne/campaign_type"
    )

    AD_FORMAT_CHOICES = [
        ("native", "Native Ad"),
        ("banner", "Banner"),
        ("interstitial", "Interstitial"),
        ("push", "Push Notification"),
        ("proximity", "Proximity Ad"),
        ("video_interstitial", "Video Interstitial"),
    ]
    format = models.CharField(max_length=20, choices=AD_FORMAT_CHOICES, default="native", verbose_name="Format")
    title = models.CharField(max_length=255,null=True,blank=True, verbose_name="Titre de l'Annonce/title")
    ad_creative_content_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="Contenu Textuel de l'Annonce",
        help_text="Texte principal ou description de l'annonce."
    )
    image = models.ImageField(upload_to="ads/", blank=True, null=True, verbose_name="Image de l'Annonce/image")
    video = models.FileField(upload_to="ads/videos/", blank=True, null=True, verbose_name="Fichier Vidéo de l'Annonce/video")
    video_url = models.URLField(blank=True, null=True, verbose_name="URL Vidéo de l'Annonce/video_url")
    link_url = models.URLField(verbose_name="URL de Destination (Clic)/link_url", help_text="URL vers laquelle l'annonce redirige les utilisateurs lorsqu'ils cliquent.")

    push_message = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Message de la notification Push",
        help_text="Texte court et percutant pour la notification push."
    )

    # Dates de la campagne publicitaire
    start_date = models.DateField(verbose_name="Début de Campagne/start_date")
    end_date = models.DateField(verbose_name="Fin de Campagne/end_date")

    # Ciblage et placement
    target_audience_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Public Cible/target_audience_description",
        help_text="Détails sur le ciblage démographique, géographique, comportemental, etc."
    )
    ad_placement_details = models.TextField(
        blank=True,
        null=True,
        verbose_name="Placement de l'Annonce/ad_placement_details",
        help_text="Emplacements spécifiques dans l'application (ex: 'Bannière en haut des pages de ville')."
    )

    # Tarification spécifique à cette campagne
    currency = models.CharField(max_length=3, default='USD', verbose_name="Devise/currency")
    cpm_price = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Taux CPM/cpm_price")
    cpc_price = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Taux CPC/cpc_price")
    cpa_price = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name="Taux CPA/cpa_price")
    package_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix Forfait/package_price")
    premium_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix Pack Premium/premium_price")

    total_agreed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Prix Total Convenu/total_agreed_price",
        help_text="Prix total fixe pour l'estimation de les campagnes à la performance."
    )
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taux de Taxe (%)/tax_rate",)

    # Suivi des performances (compteurs réels)
    impressions_count = models.PositiveIntegerField(default=0, verbose_name="Nombre d'Impressions/impressions_count")
    clicks_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de Clics/clicks_count")
    conversions_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de Conversions/conversions_count")

    # Objectifs de performance (pour les make-goods)
    performance_goal_impressions = models.PositiveIntegerField(null=True, blank=True, verbose_name="Objectif Impressions/performance_goal_impressions")
    performance_goal_clicks = models.PositiveIntegerField(null=True, blank=True, verbose_name="Objectif Clics/performance_goal_clicks")
    performance_goal_conversions = models.PositiveIntegerField(null=True, blank=True, verbose_name="Objectif Conversions/performance_goal_conversions")

    # Rapports
    REPORTING_FREQUENCY_CHOICES = [
        ("DAILY", "daily"),
        ("WEEKLY", "weekly"),
        ("MONTHLY", "monthly"),
        ("QUARTERLY", "quarterly"),
        ("YEARLY", "yearly"),
        ("PER_CAMPAIGN", "per_campaign"),
        ("ON_DEMAND", "on_demand"),
        ("AUTOMATED_DASHBOARD", "automated_dashboard"),]
    reporting_frequency = models.CharField(
        max_length=20,
        choices=REPORTING_FREQUENCY_CHOICES,
        default="MONTHLY",
        verbose_name="Fréquence de Rapports/reporting_frequency",
        help_text="Fréquence à laquelle les rapports de performance seront générés."
    )

    REPORTING_FORMAT_CHOICES = [
        ("PDF", "pdf"),
        ("CSV", "csv"),
        ("XLSX", "xlsx"),
        ("XML", "xml"),
    ]
    reporting_format = models.CharField(
        max_length=30,
        choices=REPORTING_FORMAT_CHOICES,
        default="PDF",
        verbose_name="Format de Rapports/reporting_format"
    )

    # Statut de la campagne et make-good
    AD_STATUS_CHOICES = [
        ("PENDING", "pending"),
        ("ACTIVE", "active"),
        ("COMPLETED", "completed"),
        ("CANCELLED", "cancelled"),
        ("EXPIRED", "expired"),
        ("SUSPENDED", "suspended"),
        ("FAILED", "failed"),]
    status = models.CharField(
        max_length=20,
        choices=AD_STATUS_CHOICES,
        default="PENDING",
        verbose_name="Statut Annonce/Advertisement status",
    )
    
    MAKE_GOOD_STATUS_CHOICES = [
        ("NONE", "No Make-Good Required"),
        ("PENDING", "Pending Review"),
        ("APPROVED", "Approved for Make-Good"),
        ("DELIVERED", "Make-Good Delivered"),
        ("REJECTED", "Make-Good Rejected"),
        ("COMPLETED", "Make-Good Completed"),
        ("PARTIAL", "Partial Make-Good Delivered"),
    ]
    make_good_status = models.CharField(
        max_length=20,
        choices=MAKE_GOOD_STATUS_CHOICES,
        default="NONE",
        verbose_name="Statut de Compensation/Make-Good status"
    )

    make_good_details = models.TextField(
        blank=True,
        null=True,
        verbose_name="Détails de Compensation/make_good_details",
        help_text="Description des actions de compensation (ex: prolongation de campagne, crédit)."
    )

    # Relations avec les activités/événements
    related_activity = models.ForeignKey(
        Activity, null=True, blank=True, on_delete=models.SET_NULL, related_name="ads",
        verbose_name="Activité Liée/related_activity"
    )
    related_event = models.ForeignKey(
        Event, null=True, blank=True, on_delete=models.SET_NULL, related_name="ads",
        verbose_name="Événement Lié/related_event"
    )
    
    score_bonus = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="dernière modification/updated_at")

    class Meta:
        verbose_name = "campagne Publicitaire/IOs"
        verbose_name_plural = "Campagnes Publicitaires (Ios)"
        ordering = ["-created_at"]

    def clean(self):
        errors = {}

        # Only one target: either an activity or an event
        if self.related_activity and self.related_event:
            errors["related_activity"] = "An advertisement can target either an activity or an event, not both."
            errors["related_event"] = "An advertisement can target either an activity or an event, not both."

        # Video is mandatory for video interstitial format
        if self.format == "video_interstitial" and not (self.video or self.video_url):
            errors["video"] = "A video interstitial must have either a video file or a video URL."
            errors["video_url"] = "A video interstitial must have either a video file or a video URL."

        # Start and end dates consistency
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors["end_date"] = "End date must be later than start date."

        # Contract period validation (if a contract is attached)
        if self.contract:
            contract_start = self.contract.start_date
            contract_end = self.contract.end_date
            if self.start_date < contract_start:
                errors["start_date"] = f"Start date cannot be earlier than the contract start date ({contract_start})."
            if self.end_date > contract_end:
                errors["end_date"] = f"End date cannot be later than the contract end date ({contract_end})."
        
        # Ensure that pricing fields are set correctly based on campaign_type
        # And that only relevant pricing fields are filled
        pricing_fields = {
            "CPM": "cpm_price",
            "CPC": "cpc_price",
            "CPA": "cpa_price",
            "COMBO": ("cpm_price","cpc_price","cpa_price",),
            "PACKAGE": "package_price",
            "PREMIUM": "premium_price",
        }
        if self.campaign_type == "COMBO":
            # Pour COMBO, il faut au moins 2 prix renseignés
            count = 0
            for field in pricing_fields["COMBO"]:
                if getattr(self, field) is not None:
                    count += 1
            if count < 2:
                errors["campaign_type"] = "At least two rates must be set for COMBO campaigns."
        else:
            for campaign_type, field_name in pricing_fields.items():
                if campaign_type == "COMBO":
                    continue  

                if self.campaign_type == campaign_type:
                    if getattr(self, field_name,None) is None:
                        errors[field_name] = f"{field_name.replace('_', ' ').title()} is required for {campaign_type} campaigns." 
                else:
                    if getattr(self, field_name,None) is not None:
                        errors[field_name] = f"{field_name.replace('_', ' ').title()} should only be set for {campaign_type} campaigns."



        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.title} ({self.io_reference_number})"

    def save(self, *args, **kwargs):
        if not self.pk and not self.io_reference_number:
            # Assurez-vous que le service generate_io_reference est bien défini
            self.io_reference_number = generate_io_reference()  
        self.clean()  # Run validation before saving
        super().save(*args, **kwargs)

    @property
    def location(self):
        """Retreive data (latitude, longitude) for ad."""
        if self.related_activity and self.related_activity.latitude is not None:
            return self.related_activity.latitude, self.related_activity.longitude
        if self.related_event and self.related_event.latitude is not None:
            return self.related_event.latitude, self.related_event.longitude
        return None