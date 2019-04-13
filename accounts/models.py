import json
from json import JSONDecodeError

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from requests.auth import HTTPBasicAuth

from receipt.models import Receipt


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
            self.get_new_code()

    def get_new_code(self):
        url = 'https://proverkacheka.nalog.ru:9999/v1/mobile/users/restore'
        r = requests.post(url, json={"phone": self.phone})
        if r.status_code == 204:
            return "ok"
        else:
            return "fail"

    def login_to_api(self):
        url = "https://proverkacheka.nalog.ru:9999/v1/mobile/users/login"
        r = requests.get(url, auth=HTTPBasicAuth(self.phone, self.sms_code))
        return r.status_code

    def check_existance(self, data):
        url = f"https://proverkacheka.nalog.ru:9999/v1/ofds/*/inns/*/fss/{data['fn']}/operations/1/tickets/{data['fd']}?fiscalSign={data['fp']}&date={data['time']}&sum={int(data['summ'])}"
        r = requests.get(url, auth=HTTPBasicAuth(self.phone, self.sms_code))
        print("check existance:", r.status_code, r.text)
        return r.status_code

    def get_real_receipt(self, data):
        url = f'https://proverkacheka.nalog.ru:9999/v1/inns/*/kkts/*/fss/{data["fn"]}/tickets/{data["fd"]}?fiscalSign={data["fp"]}&sendToEmail=no'
        headers = {"device-id": "web_app", "device-os": "windows"}
        print("treying to create")
        r = requests.get(url, headers=headers, auth=HTTPBasicAuth(self.phone, self.sms_code))
        print(f"status code: {r.status_code}", r.text)
        to_parse = json.loads(r.text)
        try:
            Receipt.create_from_json(to_parse, user=self.user)
        except JSONDecodeError:
            return "There was a mistake with json. Try again! "