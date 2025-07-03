# ---------------------------------------------------------------------------
#                    T e x a s  B u d d y   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   : notifications/models/company_info.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.db import models
class CompanyInfo(models.Model):
    name = models.CharField(max_length=50,null=False,blank=False)
    ein = models.CharField(max_length=20,null=True,blank=True)
    siren = models.CharField(max_length=20,null=True,blank=True)
    legal_structure = models.CharField(max_length=30,null=True, blank=True)
    vat_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=155)
    tax_info= models.CharField(max_length=6)
    tax_math = models.FloatField(null=True, blank=True)
    email = models.CharField(max_length=150,unique=True)
    phone = models.CharField(max_length=15, blank=True,null=True)
    instagram = models.CharField(max_length=50)
    is_in_texas = models.BooleanField(default=False)

    legal_notice = (
        "Texas Buddy is a registered Texas LLC | Registered in Travis County | "
    )