from datetime import datetime
from json import JSONDecodeError

from django.db import models
from django.contrib.auth.models import User
import requests

from requests.auth import HTTPBasicAuth
import json


class ReceiptData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pre_receipts')
    fd = models.CharField(max_length=16)
    fp = models.CharField(max_length=16)
    summ = models.IntegerField()
    time = models.CharField(max_length=20)
    fn = models.CharField(max_length=20)

    @classmethod
    def create_from_dict(cls, dict, user):
        ReceiptData.objects.create(fd=dict['fd'], fp=dict['fp'], summ=dict['summ'], time=dict['time'],
                                   fn=dict['fn'], user=user)

    def __str__(self):
        return self.time


class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receipts')
    time = models.CharField(max_length=20)
    items = models.TextField()
    summ = models.FloatField()
    shop = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.shop}, {self.transform_time}'

    @property
    def transform_time(self):
        return datetime.strptime(self.time, '%Y-%m-%dT%H:%M:%S').strftime('%m %B %Y %H:%M')

    @staticmethod
    def register_in_api(email, name, phone):
        url = "https://proverkacheka.nalog.ru:9999/v1/mobile/users/signup"
        payload = {"email": email, "name": name, "phone": phone}
        r = requests.post(url, json=payload)
        if r.status_code == 204:
            print("Great! SMS")
        else:
            print(r.text, r.content)
            print("not good")

    @staticmethod
    def login_to_api(phone, sms):
        url = "https://proverkacheka.nalog.ru:9999/v1/mobile/users/login"
        r = requests.get(url, auth=HTTPBasicAuth(phone, sms))
        print(r.status_code, r.text, r.content)

    @staticmethod
    def check_existance(data, user):
        url = f"https://proverkacheka.nalog.ru:9999/v1/ofds/*/inns/*/fss/{data['fn']}/operations/1/tickets/{data['fd']}?fiscalSign={data['fp']}&date={data['time']}&sum={int(data['summ'])}"
        r = requests.get(url, auth=HTTPBasicAuth(user.profile.phone, user.profile.sms_code))
        print("checked existance:", r.status_code, r.text, r.content)

    @staticmethod
    def get_new_code(phone):
        url = 'https://proverkacheka.nalog.ru:9999/v1/mobile/users/restore'
        r = requests.post(url, json={"phone": phone})

    @staticmethod
    def get_real_receipt(data, user):
        url = f'https://proverkacheka.nalog.ru:9999/v1/inns/*/kkts/*/fss/{data["fn"]}/tickets/{data["fd"]}?fiscalSign={data["fp"]}&sendToEmail=no'
        headers = {"device-id": "web_app", "device-os": "windows"}
        print("treying to create")
        r = requests.get(url, headers=headers, auth=HTTPBasicAuth(user.profile.phone, user.profile.sms_code))
        print(f"status code: {r.status_code}", r.text)
        to_parse = json.loads(r.text)
        try:
            Receipt.create_from_json(to_parse, user=user)
        except JSONDecodeError:
            return "There was a mistake with json. Try again! "

    @classmethod
    def create_from_json(cls, json, user):
        Receipt.objects.get_or_create(user=user, time=json['document']['receipt']['dateTime'], items=json['document']['receipt']['items'],
                               summ=json['document']['receipt']['totalSum'] / 100, shop=json['document']['receipt']['user'])





