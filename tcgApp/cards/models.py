import datetime

from django.db import models
from django.utils import timezone


class Collection(models.Model):
    collection_name = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    def __str__(self):
        return self.collection_name

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Card(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    def __str__(self):
        return self.card_name