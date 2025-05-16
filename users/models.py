from django.db import models
from django_countries.fields import CountryField

# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField( max_length=150)
    phone = models.CharField(max_length=12, blank=True, null=True)
    address = models.CharField(max_length=200,null=True,blank=True)
    country = CountryField( null=False, blank=False)
    timestamp = models.DateTimeField(auto_now=True)
