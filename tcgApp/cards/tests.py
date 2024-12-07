import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Collection


class CollectionModelTests(TestCase):
    def test_was_published_recently_with_future_collection(self):
        """
        was_published_recently() returns False for collections whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_collection = Collection(pub_date=time)
        self.assertIs(future_collection.was_published_recently(), False)

    def test_was_published_recently_with_old_collection(self):
        """
        was_published_recently() returns False for collections whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_collection = Collection(pub_date=time)
        self.assertIs(old_collection.was_published_recently(), False)

    def test_was_published_recently_with_recent_collection(self):
        """
        was_published_recently() returns True for collections whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_collection = Collection(pub_date=time)
        self.assertIs(recent_collection.was_published_recently(), True)

def create_collection(collection_name, days):
    """
    Create a collection with the given `collection_name` and published the
    given number of `days` offset to now (negative for collections published
    in the past, positive for collections that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Collection.objects.create(collection_name=collection_name, pub_date=time)

class CollectionIndexViewTests(TestCase):
    def test_no_collections(self):
        """
        If no collections exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("cards:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No collections are available.")
        self.assertQuerySetEqual(response.context["latest_collection_list"], [])

    def test_past_collection(self):
        """
        Collections with a pub_date in the past are displayed on the
        index page.
        """
        collection = create_collection(collection_name="Past collection.", days=-30)
        response = self.client.get(reverse("cards:index"))
        self.assertQuerySetEqual(
            response.context["latest_collection_list"],
            [collection],
        )

    def test_future_collection(self):
        """
        Collections with a pub_date in the future aren't displayed on
        the index page.
        """
        create_collection(collection_name="Future collection.", days=30)
        response = self.client.get(reverse("cards:index"))
        self.assertContains(response, "No collections are available.")
        self.assertQuerySetEqual(response.context["latest_collection_list"], [])

    def test_future_collection_and_past_collection(self):
        """
        Even if both past and future collections exist, only past collections
        are displayed.
        """
        collection = create_collection(collection_name="Past collection.", days=-30)
        create_collection(collection_name="Future collection.", days=30)
        response = self.client.get(reverse("cards:index"))
        self.assertQuerySetEqual(
            response.context["latest_collection_list"],
            [collection],
        )

    def test_two_past_collections(self):
        """
        The collections index page may display multiple collections.
        """
        collection1 = create_collection(collection_name="Past collection 1.", days=-30)
        collection2 = create_collection(collection_name="Past collection 2.", days=-5)
        response = self.client.get(reverse("cards:index"))
        self.assertQuerySetEqual(
            response.context["latest_collection_list"],
            [collection2, collection1],
        )

class CollectionDetailViewTests(TestCase):
    def test_future_collection(self):
        """
        The detail view of a collection with a pub_date in the future
        returns a 404 not found.
        """
        future_collection = create_collection(collection_name="Future collection.", days=5)
        url = reverse("cards:detail", args=(future_collection.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_collection(self):
        """
        The detail view of a collection with a pub_date in the past
        displays the collection's text.
        """
        past_collection = create_collection(collection_name="Past Collection.", days=-5)
        url = reverse("cards:detail", args=(past_collection.id,))
        response = self.client.get(url)
        self.assertContains(response, past_collection.collection_name)