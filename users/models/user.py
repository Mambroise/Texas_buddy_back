# ---------------------------------------------------------------------------
#                           TEXAS BUDDY   ( 2 0 2 5 )
# ---------------------------------------------------------------------------
# File   :users/models/user.py
# Author : Morice
# ---------------------------------------------------------------------------


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django_countries.fields import CountryField
from django.utils import timezone
from activities.models import Category

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    country = CountryField()
    sign_up_number = models.CharField(max_length=100)
    first_ip = models.GenericIPAddressField(null=True, blank=True)
    second_ip = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    can_set_password = models.BooleanField(default=False)
        # Consentement pour l'utilisation des données personnelles à des fins publicitaires
    has_data_consent = models.BooleanField(
        default=False,
        verbose_name="Consentement pour les données"
    )

    # Centres d'intérêt de l'utilisateur, liés aux catégories d'activités
    interests = models.ManyToManyField(
        Category,
        blank=True,
        related_name="interested_users",
        verbose_name="interests"
    )

    # Required fields for admin
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
