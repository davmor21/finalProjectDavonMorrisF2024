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


class Card(models.Model):
    collection = models.ForeignKey('Collection', on_delete=models.CASCADE)
    card_name = models.CharField(max_length=200)
    card_type = models.CharField(max_length=200, blank=True)  # Type of card (Creature, Instant, etc.)
    color = models.CharField(max_length=100, blank=True)  # Color of the card (e.g., Red, Green)
    mana_cost = models.CharField(max_length=100, blank=True)  # Mana cost (e.g., {3}{R}, {1}{G}{G}, etc.)
    set_name = models.CharField(max_length=100, blank=True)  # The set the card is from (e.g., Innistrad Remastered)
    image_url = models.URLField(blank=True)  # URL of the card image
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Price in USD

    def __str__(self):
        return self.card_name