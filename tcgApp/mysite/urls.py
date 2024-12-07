from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cards/", include("cards.urls")),
    path("users/", include("users.urls")),
    path('', include("cards.urls")),
]