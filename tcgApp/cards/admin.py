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

    # Custom method to show the user ID
    def user_id(self, obj):
        return obj.user.id

    user_id.admin_order_field = 'user'
    user_id.short_description = 'User ID'

    list_display = ["collection_name", "user", "user_id", "pub_date", "was_published_recently"]  # Add "user" here
    list_filter = ["pub_date", "user"]  # You can also filter by "user"
    search_fields = ["collection_name", "user__username"]  # Enable search by "user's username"

class CardAdmin(admin.ModelAdmin):
    list_display = ["card_name", "card_type", "color", "mana_cost", "set_name", "price_usd"]
    search_fields = ["card_name", "card_type", "set_name"]

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Card, CardAdmin)
