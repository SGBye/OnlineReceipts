from datetime import datetime
from json import JSONDecodeError

from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.contrib.auth.models import User
import requests

from requests.auth import HTTPBasicAuth
import json


class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receipts')
    time = models.CharField(max_length=20)
    items = models.TextField()
    summ = models.FloatField()
    shop = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'time'], name='unique_receipt')
        ]

    def __str__(self):
        return f'{self.shop}, {self.transform_time}'

    @property
    def transform_time(self):
        return datetime.strptime(self.time, '%Y-%m-%dT%H:%M:%S').strftime('%m %B %Y %H:%M')

    @classmethod
    def create_from_json(cls, json, user):
        try:
            Receipt.objects.get_or_create(user=user, time=json['document']['receipt']['dateTime'], items=json['document']['receipt']['items'],
                               summ=json['document']['receipt']['totalSum'] / 100, shop=json['document']['receipt']['user'])
        except IntegrityError:
            raise ValidationError("Such receipt already exists")





