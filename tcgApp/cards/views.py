from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
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
    latest_collection_list = Collection.objects.order_by("-pub_date")[:5]
    return render(request, 'cards/index.html', {'latest_collection_list': latest_collection_list})


class DetailView(LoginRequiredMixin, generic.DetailView):
    login_url = "/users/login/"
    redirect_field_name = 'redirect_to'
    model = Collection
    template_name = "cards/detail.html"

    def get_queryset(self):
        """
        Excludes any collections that aren't published yet.
        """
        return Collection.objects.filter(pub_date__lte=timezone.now())


class ResultsView(LoginRequiredMixin, generic.DetailView):
    login_url = "/users/login/"
    redirect_field_name = 'redirect_to'
    model = Collection
    template_name = "cards/results.html"


@login_required(login_url="/users/login/")
def submit(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)

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

    return render(request, "cards/detail.html", {"collection": collection})



@login_required(login_url="/users/login/")
def remove_collection(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
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
            collection.user = request.user  # Optionally associate with the logged-in user
            collection.pub_date = timezone.now()  # Set current timestamp as publish date
            collection.save()
            return redirect('cards:index')  # Redirect to the homepage after saving the new collection
    else:
        # If the request is GET, show an empty form
        form = CollectionForm()

    return render(request, 'cards/add_collection.html', {'form': form})

@csrf_exempt
def set_theme(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Get the data from the POST request
            theme = data.get('theme')
            if theme not in ['light', 'dark']:
                return JsonResponse({'error': 'Invalid theme'}, status=400)

            # Store the theme in the session
            request.session['theme'] = theme
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid data format'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)