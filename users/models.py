# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :texasbuddy/users/models.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField


# Create your models here.
class User(AbstractUser):
    phone = models.CharField(max_length=12, blank=True, null=True)
    address = models.CharField(max_length=200,null=True,blank=True)
    country = CountryField( null=False, blank=False)
    sign_up_number = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)
