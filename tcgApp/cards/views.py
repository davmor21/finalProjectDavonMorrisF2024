from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Card
import requests
from django import forms
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Card, Collection

@login_required(login_url="/users/login/")
def IndexView(request):
    # Filter collections by logged-in user
    latest_collection_list = Collection.objects.filter(user=request.user).order_by("-pub_date")[:5]
    return render(request, 'cards/index.html', {'latest_collection_list': latest_collection_list})


class CollectionView(LoginRequiredMixin, generic.DetailView):
    login_url = "/users/login/"
    redirect_field_name = 'redirect_to'
    model = Collection
    template_name = "cards/collection.html"

    def get_queryset(self):
        """
        Filters collections to only include those belonging to the logged-in user.
        """
        return Collection.objects.filter(pub_date__lte=timezone.now(), user=self.request.user)



@login_required(login_url="/users/login/")
def submit(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id, user=request.user)  # Ensure ownership

    if request.method == "POST":
        # Step 1: Handle deletions
        delete_card_ids = request.POST.getlist("delete_card_ids[]")
        if delete_card_ids:
            # Delete cards that match the IDs in delete_card_ids for this collection
            Card.objects.filter(id__in=delete_card_ids, collection=collection).delete()

        # Step 2: Handle adding new cards
        new_card_names = request.POST.getlist("new_card_name[]")
        new_card_quantities = request.POST.getlist("new_card_quantity[]")
        for name, quantity in zip(new_card_names, new_card_quantities):
            if name:  # Add only if a name is provided
                Card.objects.create(
                    collection=collection,
                    card_name=name,
                    quantity=int(quantity)
                )

        # Step 3: Update quantities for existing cards
        for card in collection.card_set.all():
            quantity_field_name = f"quantity_{card.id}"
            if quantity_field_name in request.POST:
                new_quantity = request.POST.get(quantity_field_name)
                if new_quantity is not None:
                    card.quantity = int(new_quantity)
                    card.save()

    return render(request, "cards/collection.html", {"collection": collection})




@login_required(login_url="/users/login/")
def remove_collection(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id, user=request.user)  # Ensure ownership
    if request.method == "POST":
        collection.delete()  # Delete the collection
        return redirect('cards:index')  # Redirect back to the home page after deletion
    else:
        return redirect('cards:index')  # Redirect if method is not POST


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['collection_name']  # Only ask for the collection name in the form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['collection_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['collection_name'].label = "Collection Name"

@login_required(login_url="/users/login/")
def add_collection(request):
    if request.method == 'POST':
        # Handling form submission
        form = CollectionForm(request.POST)
        if form.is_valid():
            # Create a new collection
            collection = form.save(commit=False)
            collection.user = request.user
            collection.pub_date = timezone.now()
            collection.save()
            return redirect('cards:index')
    else:
        # If the request is GET, show an empty form
        form = CollectionForm()

    return render(request, 'cards/add_collection.html', {'form': form})

@login_required
def user_collections(request):
    collections = Collection.objects.filter(user=request.user)  # Filter by logged-in user
    return render(request, 'cards/collection.html', {'collections': collections})


def fetch_card_data(card_name):
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"
    response = requests.get(url)
    data = response.json()

    # Handle if the card is not found
    if 'error' in data:
        return None

    # Extract card details
    card_info = {
        'card_name': data['name'],
        'card_type': data['type_line'],
        'color': ', '.join(data['colors']) if 'colors' in data else 'N/A',
        'mana_cost': data['mana_cost'] if 'mana_cost' in data else 'N/A',
        'set_name': data['set_name'],
        'image_url': data['image_uris']['normal'] if 'image_uris' in data else '',
        'price_usd': data['prices']['usd'] if 'usd' in data['prices'] else 'N/A',
    }

    return card_info

class AddCardForm(forms.Form):
    card_name = forms.CharField(max_length=255, label="Card Name")

# Function to handle adding a new card
def add_card_to_collection(request, collection_id):
    collection = Collection.objects.get(pk=collection_id)

    if request.method == 'POST':
        form = AddCardForm(request.POST)
        if form.is_valid():
            card_name = form.cleaned_data['card_name']

            # Fetch card data from Scryfall
            card_data = fetch_card_data(card_name)

            if card_data:
                # Create and save the card
                card = Card(
                    collection=collection,
                    card_name=card_data['card_name'],
                    card_type=card_data['card_type'],
                    color=card_data['color'],
                    mana_cost=card_data['mana_cost'],
                    set_name=card_data['set_name'],
                    image_url=card_data['image_url'],
                    price_usd=card_data['price_usd']
                )
                card.save()

                return redirect('cards:collection', collection_id=collection.id)
            else:
                # Handle the case where card is not found
                form.add_error('card_name', 'Card not found in Scryfall API')

    else:
        form = AddCardForm()

    return render(request, 'cards/add_card.html', {'form': form, 'collection': collection})

