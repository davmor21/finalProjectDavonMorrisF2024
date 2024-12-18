import logging
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Card, Collection
from django import forms
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import requests
import json

# Set up logger
logger = logging.getLogger(__name__)

@login_required(login_url="/users/login/")
def IndexView(request):
    logger.info("User '%s' is accessing the index view.", request.user)
    # Filter collections by logged-in user
    latest_collection_list = Collection.objects.filter(user=request.user).order_by("-pub_date")[:5]
    logger.info("Fetched latest collections for user '%s'.", request.user)
    return render(request, 'cards/index.html', {'latest_collection_list': latest_collection_list})

class CollectionView(LoginRequiredMixin, generic.DetailView):
    login_url = "/users/login/"
    redirect_field_name = 'redirect_to'
    model = Collection
    template_name = "cards/collection.html"

    def get_queryset(self):
        logger.info("User '%s' is viewing a collection.", self.request.user)
        return Collection.objects.filter(pub_date__lte=timezone.now(), user=self.request.user)

@login_required(login_url="/users/login/")
def submit(request, collection_id):
    logger.info("User '%s' is submitting changes to collection '%d'.", request.user, collection_id)
    collection = get_object_or_404(Collection, pk=collection_id, user=request.user)  # Ensure ownership

    if request.method == "POST":
        logger.info("Processing POST request for collection '%d'.", collection_id)

        # Step 1: Handle deletions
        delete_card_ids = request.POST.getlist("delete_card_ids[]")
        if delete_card_ids:
            logger.info("Deleting cards with IDs: %s", delete_card_ids)
            Card.objects.filter(id__in=delete_card_ids, collection=collection).delete()

        # Step 2: Handle adding new cards
        new_card_names = request.POST.getlist("new_card_name[]")
        new_card_quantities = request.POST.getlist("new_card_quantity[]")
        for name, quantity in zip(new_card_names, new_card_quantities):
            if name:  # Add only if a name is provided
                logger.info("Adding new card: %s with quantity %d", name, quantity)
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
                    logger.info("Updating card '%d' quantity to %d.", card.id, new_quantity)
                    card.quantity = int(new_quantity)
                    card.save()

    return render(request, "cards/collection.html", {"collection": collection})

@login_required(login_url="/users/login/")
def remove_collection(request, collection_id):
    logger.info("User '%s' is requesting to remove collection '%d'.", request.user, collection_id)
    collection = get_object_or_404(Collection, pk=collection_id, user=request.user)  # Ensure ownership
    if request.method == "POST":
        logger.info("Removing collection '%d'.", collection_id)
        collection.delete()  # Delete the collection
        return redirect('cards:index')  # Redirect back to the home page after deletion
    else:
        logger.warning("Remove collection request for collection '%d' was not POST.", collection_id)
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
    logger.info("User '%s' is adding a new collection.", request.user)
    if request.method == 'POST':
        # Handling form submission
        form = CollectionForm(request.POST)
        if form.is_valid():
            # Create a new collection
            collection = form.save(commit=False)
            collection.user = request.user
            collection.pub_date = timezone.now()
            collection.save()
            logger.info("New collection '%s' created for user '%s'.", collection.collection_name, request.user)
            return redirect('cards:index')
    else:
        # If the request is GET, show an empty form
        form = CollectionForm()

    return render(request, 'cards/add_collection.html', {'form': form})

@login_required
def user_collections(request):
    logger.info("User '%s' is viewing their collections.", request.user)
    collections = Collection.objects.filter(user=request.user)  # Filter by logged-in user
    return render(request, 'cards/collection.html', {'collections': collections})

# Mapping of color abbreviations to full names
COLOR_MAPPING = {
    'U': 'Blue',
    'W': 'White',
    'B': 'Black',
    'R': 'Red',
    'G': 'Green',
    'C': 'Colorless',  # For colorless cards
}

def get_full_color_names(colors):
    """
    Converts a list of color abbreviations to their full names.
    """
    if not colors:
        return 'N/A'
    return ', '.join([COLOR_MAPPING.get(color, color) for color in colors])


def fetch_card_data(card_name):
    logger.info("Fetching card data for card name '%s'.", card_name)
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"
    response = requests.get(url)
    data = response.json()

    # Handle if the card is not found
    if 'error' in data:
        logger.warning("Card '%s' not found in Scryfall.", card_name)
        return None

    # Extract card details, providing defaults if the data is missing
    card_info = {
        'card_name': data.get('name', 'N/A'),  # Card name, default 'N/A' if missing
        'card_type': data.get('type_line', 'N/A'),  # Card type, default 'N/A' if missing
        'color': get_full_color_names(data.get('colors', [])),  # Convert color abbreviations to full names
        'mana_cost': data.get('mana_cost', 'N/A'),  # Mana cost, default 'N/A' if missing
        'set_name': data.get('set_name', 'N/A'),  # Set name, default 'N/A' if missing
        'image_url': data.get('image_uris', {}).get('normal', ''),  # Image URL, default '' if missing
        'price_usd': data.get('prices', {}).get('usd', 0.0),  # Ensure price is set to 0.0 if missing
    }

    # Ensure price_usd is never None or Null and defaults to 0 if necessary
    card_info['price_usd'] = card_info.get('price_usd', 0.0) or 0.0

    logger.info("Fetched data for card '%s': %s", card_name, card_info)
    return card_info




@login_required
def add_cards_to_collection(request, collection_id):
    try:
        if request.method == 'POST':
            collection = get_object_or_404(Collection, id=collection_id)

            # Parse the JSON data
            data = json.loads(request.body)
            selected_cards = data.get('selected_cards', [])

            if not selected_cards:
                return JsonResponse({'status': 'error', 'message': 'No cards selected'}, status=400)

            # Process each selected card and add it to the collection
            for card_data in selected_cards:
                card_name = card_data.get('name')
                card_quantity = card_data.get('quantity', 1)

                # Fetch additional card data
                card_info = fetch_card_data(card_name)
                if not card_info:
                    logger.error(f"Failed to fetch data for card: {card_name}")
                    continue  # Skip this card if fetch fails

                # Extract details from the fetched data
                card_type = card_info.get('card_type', '')
                card_color = card_info.get('color', '')
                mana_cost = card_info.get('mana_cost', '')
                set_name = card_info.get('set_name', '')
                price_usd = card_info.get('price_usd', '')
                card_image_url = card_info.get('image_url', '')

                # Create or update the card in the collection
                card, created = Card.objects.get_or_create(
                    card_name=card_name,
                    collection=collection,
                    defaults={
                        'card_type': card_type,
                        'color': card_color,
                        'mana_cost': mana_cost,
                        'set_name': set_name,
                        'price_usd': price_usd,
                        'image_url': card_image_url,
                        'quantity': card_quantity
                    }
                )

                # If the card already exists, update the quantity
                if not created:
                    card.quantity += card_quantity
                    card.save()

                logger.info(f"Card {'created' if created else 'updated'}: {card_name}, Quantity: {card.quantity}")

            return JsonResponse({'status': 'success', 'message': 'Cards added to collection'})

        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    except Exception as e:
        logger.error(f"Error occurred while adding cards to collection '{collection_id}': {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def collection_detail(request, collection_id):
    logger.info("User '%s' is viewing collection detail for collection '%d'.", request.user, collection_id)
    # Get the collection object
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)

    # Handle the "Save" button (updating quantities)
    if request.method == "POST":
        if 'save_quantities' in request.POST:
            logger.info("Saving quantities for cards in collection '%d'.", collection_id)
            # Update quantities of cards
            for card in collection.card_set.all():
                quantity = request.POST.get(f'quantity_{card.id}')
                if quantity:
                    card.quantity = int(quantity)
                    card.save()
            return redirect('cards:collection_detail', collection_id=collection.id)

        # Handle "Add selected cards" request
        if 'selected_cards' in request.POST:
            logger.info("Adding selected cards to collection '%d'.", collection_id)
            selected_cards = request.POST.getlist('selected_cards')
            for selected_card in selected_cards:
                card_data = selected_card.split(';')  # Example: card_name;image_url;price_usd
                card_name, image_url, price_usd = card_data

                # Check if the card already exists in the collection
                card, created = Card.objects.get_or_create(
                    collection=collection,
                    card_name=card_name,
                    defaults={'image_url': image_url, 'price_usd': price_usd}
                )
                if not created:
                    logger.info("Card '%s' already exists in collection '%d'. Incrementing quantity.", card_name, collection_id)
                    card.quantity += 1  # If card already exists, increment quantity
                    card.save()

            return redirect('cards:collection_detail', collection_id=collection.id)

    return render(request, 'cards/collection.html', {'collection': collection})

@csrf_exempt
def remove_card_from_collection(request, collection_id, card_id):
    logger.info("User '%s' is requesting to remove card '%d' from collection '%d'.", request.user, card_id, collection_id)
    # Get the collection and card objects
    collection = get_object_or_404(Collection, pk=collection_id)
    card = get_object_or_404(Card, pk=card_id, collection=collection)  # Ensure the card belongs to the collection

    # Delete the card (this removes the card from the collection)
    card.delete()
    logger.info("Card '%d' removed from collection '%d'.", card_id, collection_id)

    # Return a success response in JSON format
    return JsonResponse({"status": "success", "message": "Card removed successfully"})


def fetch_parsed_mana_cost(mana_cost):
    url = f"https://api.scryfall.com/symbology/parse-mana?cost={mana_cost}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def parse_mana_cost(mana_cost):
    # Call Scryfall API to parse the mana cost
    parsed_data = fetch_parsed_mana_cost(mana_cost)

    if parsed_data:
        # Extract the normalized cost and the colors involved
        normalized_cost = parsed_data['cost']
        colors = parsed_data['colors']
        cmc = parsed_data['cmc']
        colorless = parsed_data['colorless']
        monocolored = parsed_data['monocolored']
        multicolored = parsed_data['multicolored']

        # Render the normalized mana cost (e.g., {X}{U}{R})
        return normalized_cost, colors, cmc, colorless, monocolored, multicolored
    else:
        return None
