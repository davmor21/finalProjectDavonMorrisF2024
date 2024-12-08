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
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=200)
    card_type = models.CharField(max_length=100, blank=True)  # Store card type (creature, instant, etc.)
    color = models.CharField(max_length=50, blank=True)  # Store color (Red, Green, etc.)
    mana_cost = models.CharField(max_length=50, blank=True)  # Store mana cost (e.g., {1}{G}, etc.)
    set_name = models.CharField(max_length=100, blank=True)  # Store the set name (e.g., Core Set 2020)
    image_url = models.URLField(blank=True)  # Store image URL of the card
    price_usd = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Store card price
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.card_name

