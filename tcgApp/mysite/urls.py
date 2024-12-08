from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("cards.urls", namespace="cards")),
    path("users/", include("users.urls")),
]