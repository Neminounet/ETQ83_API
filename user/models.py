from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from availability.models import Availability, RendezVous


class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **kwargs):
        if not email:
            raise ValueError("Vous devez entrer une adresse email valide.")
        if not first_name and last_name:
            raise ValueError(
                "Vous devez entrer votre prénom ainsi que votre nom.")
        else:
            user = self.model(
                email=self.normalize_email(email),
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            user.save()
            return user

    def create_superuser(self, email, first_name, last_name, password=None, **kwargs):
        user = self.create_user(email=email, password=password,
                                first_name=first_name, last_name=last_name)
        user.is_superuser = True
        user.is_premium = True
        user.is_staff = True
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True, max_length=255, blank=False, verbose_name="Adresse Email")
    first_name = models.CharField(
        blank=False, max_length=255, default="", verbose_name="Prénom")
    last_name = models.CharField(
        blank=False, max_length=255, default="", verbose_name="Nom de famille")
    telephone = models.CharField(max_length=10, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profile_images/', null=True, blank=True, default="default_images/user.png")
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = MyUserManager()

    def delete(self, *args, **kwargs):
        rendezvous = RendezVous.objects.filter(user=self)

        for rdv in rendezvous:
            rdv.availability.delete()
            rdv.delete()

        super().delete(*args, **kwargs)
