# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :ads/manager.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
from django.utils import timezone

class AdLogQuerySet(models.QuerySet):
    def by_contract(self, contract_id):
        return self.filter(advertisement__contract_id=contract_id)

    def by_partner(self, partner_id):
        return self.filter(advertisement__contract__partner_id=partner_id)
    
    def by_advertisement(self, ad_id):
        return self.filter(advertisement_id=ad_id)

    def between_dates(self, start_date, end_date):
        return self.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
