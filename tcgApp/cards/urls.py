from django.urls import path
from . import views

app_name = "cards"
urlpatterns = [
    path("", views.IndexView, name="index"),
    path("<int:pk>/", views.CollectionView.as_view(), name="detail"),
    path("<int:collection_id>/submit/", views.submit, name="submit"),
    path("remove_collection/<int:collection_id>/", views.remove_collection, name="remove_collection"),
    path('add_collection/', views.add_collection, name='add_collection'),
    path('add_cards_to_collection/<int:collection_id>/', views.add_cards_to_collection, name='add_cards_to_collection'),
    path('remove_card_from_collection/<int:collection_id>/<int:card_id>/', views.remove_card_from_collection, name='remove_card_from_collection'),
]
