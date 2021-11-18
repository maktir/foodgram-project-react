from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import Follow
from users.serializers import (RegistrySerializer, SubscriptionListSerializer,
                               SubscriptionSerializer, UserSerializer)

from . import serializers
from .filters import RecipeFilter
from .models import (Cart, Favorite, Ingredient, IngredientsOfRecipe, Recipe,
                     Tag)
from .pagination import LimitPagination
from .permissions import RecipePermissions
from .serializers import CartSerializer, FavoriteSerializer

User = get_user_model()


class ListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return RegistrySerializer

    @action(detail=False,
            methods=['GET'],
            url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False,
            methods=['POST'],
            url_path='set_password',
            permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        if not request.user.check_password(
                request.data.get('current_password')
        ):
            return Response({'current_password': ['Wrong password.']},
                            status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(request.data.get('new_password'))
        request.user.save()
        return Response({'password': 'Password successfully updated'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        users = request.user.follower.all()
        recipes_limit = request.GET.get('recipes_limit', '')
        serializer = SubscriptionSerializer(
            users,
            context={'request': request},
            many=True
        )
        page = self.paginate_queryset(users)
        if page is not None:
            if not recipes_limit.isdigit():
                return self.get_paginated_response(serializer.data)
            else:
                for item in serializer.data:
                    recipes = item['recipes'][:int(recipes_limit)]
                    item['recipes'] = recipes
                return self.get_paginated_response(serializer.data)
        else:
            return Response(serializer.data)

    @action(
        methods=['GET', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated, ])
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        recipes_limit = request.query_params.get('recipes_limit', '')
        if request.method == 'GET':
            Follow.objects.create(user=request.user, author=author)
            serializer = SubscriptionListSerializer(
                author,
                context={'request': request}
            )
            filtered_data = serializer.data
            if not recipes_limit.isdigit():
                return Response(
                    filtered_data, status=status.HTTP_201_CREATED)
            recipes = serializer.data['recipes'][:int(recipes_limit)]
            filtered_data['recipes'] = recipes
            return Response(filtered_data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                Follow.objects.get(user=request.user,
                                   author=author).delete()
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [RecipePermissions]
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.RecipeReadSerializer
        return serializers.RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['GET', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk).id
        user = request.user.id
        if request.method == 'GET':
            data = {'user': user, 'recipe': recipe}
            context = {'request': request}
            serializer = FavoriteSerializer(data=data,
                                            context=context)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                Favorite.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    {'errors': 'This recipe is not in your favorites.'},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['GET', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk).id
        user = request.user.id
        if request.method == 'GET':
            data = {'user': user, 'recipe': recipe}
            context = {'request': request}
            serializer = CartSerializer(data=data,
                                        context=context)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                Cart.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    {'errors': 'This recipe is not in your shopping cart.'},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['GET'],
            permission_classes=(permissions.IsAuthenticated, ))
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = user.carted.all()
        structured_cart = {}

        for item in shopping_cart:
            recipe = item.recipe
            ingredients = IngredientsOfRecipe.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                if name not in structured_cart:
                    structured_cart[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    structured_cart[name]['amount'] = (structured_cart[name]['amount'] + amount)

        file_data = []
        for item in structured_cart:
            file_data.append(
                f'{item} - {structured_cart[item]["amount"]} '
                f'{structured_cart[item]["measurement_unit"]} \r\n'
            )

        response = HttpResponse(file_data,
                                'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response


class IngredientViewSet(ListRetrieveViewSet):
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(ListRetrieveViewSet):
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
