from django.contrib import admin

from .models import Recipe, Ingredient, IngredientsOfRecipe, Tag, Favorite, Cart
from users.models import Follow

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientsOfRecipe)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(Cart)
admin.site.register(Follow)