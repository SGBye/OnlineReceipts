import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=100, unique=True)
    is_registered = models.BooleanField(default=False)
    is_logon = models.BooleanField(default=False)
    sms_code = models.CharField(blank=True, max_length=10)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance, phone=instance.phone)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def register_in_api(self):
        url = settings.API_REGISTER_URL
        payload = {"email": self.user.email, "name": self.user.username, "phone": self.phone}

        r = requests.post(url, json=payload)
        if r.status_code != 204:
            raise ValidationError("Unfortunately something went wrong. Try again!")
