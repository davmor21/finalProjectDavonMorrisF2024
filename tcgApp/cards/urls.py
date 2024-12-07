from django.urls import path

from . import views

app_name = "cards"
urlpatterns = [
    path("", views.IndexView, name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:collection_id>/submit/", views.submit, name="submit"),
    path("remove_collection/<int:collection_id>/", views.remove_collection, name="remove_collection"),
    path('add_collection/', views.add_collection, name='add_collection'),
    path('set_theme/', views.set_theme, name='set_theme'),  # Add this line
]