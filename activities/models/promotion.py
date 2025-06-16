# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/activities/models/promotion.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from django.utils import timezone

class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    # Lien vers Activity ou Event (un seul à la fois)
    activity = models.ForeignKey("activities.Activity", on_delete=models.CASCADE, null=True, blank=True, related_name="promotions")
    event = models.ForeignKey("activities.Event", on_delete=models.CASCADE, null=True, blank=True, related_name="promotions")

    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(activity__isnull=False, event__isnull=True) |
                    models.Q(activity__isnull=True, event__isnull=False)
                ),
                name='promotion_link_to_one_model_only'
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.get_discount_type_display()} - {self.amount})"

    def is_currently_active(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
