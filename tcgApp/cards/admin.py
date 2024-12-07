from django.contrib import admin

from .models import Card, Collection

class CardInline(admin.TabularInline):
    model = Card
    extra = 1
class CollectionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["collection_name"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [CardInline]
    list_display = ["collection_name", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["collection_name"]


admin.site.register(Collection, CollectionAdmin)
