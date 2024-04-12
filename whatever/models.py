from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext as _


class UserProfile(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username", "password")

    email = models.EmailField(_("email address"), unique=True)
    password = models.CharField(_("password"), max_length=128, blank=True, null=True)
    pubkey = models.CharField(_("wallet address"), max_length=128, blank=True, null=True)
    privkey = models.CharField(_("private key"), max_length=128, blank=True, null=True)
    seed = models.CharField(_("seed"), max_length=128, blank=True, null=True)


class House(models.Model):
    city = models.CharField(max_length=100)
    rooms = models.IntegerField()
    year_of_construction = models.IntegerField()
    images = models.ImageField(upload_to='houses/', blank=True, null=True)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True)


class Sale(models.Model):
    is_sold = models.BooleanField(default=False)
    auction_end_time = models.DateTimeField(default=timezone.now() + timedelta(days=21))
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="sale")
    waiting_list = models.ManyToManyField(UserProfile, related_name="waiting_list", blank=True)
