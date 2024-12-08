import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Collection(models.Model):
    collection_name = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.collection_name

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    @property
    def total_price(self):
        # Use reverse relationship to access cards
        return sum(card.price_usd or 0 for card in self.card_set.all())


class Card(models.Model):
    card_name = models.CharField(max_length=255)
    card_type = models.CharField(max_length=255)
    color = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(blank=True)  # URL of the card image
    mana_cost = models.CharField(max_length=255, blank=True)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    set_name = models.CharField(max_length=255, blank=True)
    quantity = models.IntegerField(default=1)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    def __str__(self):
        return self.card_name

