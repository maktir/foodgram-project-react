from django.contrib import admin

from .models import (Cart, Favorite, Ingredient, IngredientsOfRecipe, Recipe,
                     Tag, TagsOfRecipe)

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientsOfRecipe)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(Cart)
admin.site.register(TagsOfRecipe)
