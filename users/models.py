import logging

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models

logger = logging.getLogger('users')


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        logger.info(f'User created with email: {email}')
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            logger.error('Superuser must have is_staff=True.')
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            logger.error('Superuser must have is_superuser=True.')
            raise ValueError('Superuser must have is_superuser=True.')
        logger.info(f'Superuser created with email: {email}')
        return self.create_user(email, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email Address")
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    phone_number = PhoneNumberField(region="IR", verbose_name="Phone Number")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Birth Date")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f" {self.email}"