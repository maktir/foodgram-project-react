from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router_api = routers.DefaultRouter()
router_api.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router_api.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router_api.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
router_api.register(
    r'users',
    UserViewSet,
    basename='users'
)
urlpatterns = [
    path('', include(router_api.urls))
]
