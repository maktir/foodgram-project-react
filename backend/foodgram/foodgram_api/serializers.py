from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import UserSerializer

from .models import (Cart, Favorite, Ingredient, IngredientsOfRecipe, Recipe,
                     Tag)

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        read_only_fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsOfRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsOfRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class SetIngredientsToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsOfRecipe
        fields = ('id', 'amount')

    def validate_amount(self, amount):
        if int(amount) < 1:
            raise serializers.ValidationError("Amount can't be less than 1.")
        return amount


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_ingredients(self, recipe):
        ingredients_of_recipe = IngredientsOfRecipe.objects.filter(
            recipe=recipe
        )
        return IngredientsOfRecipeSerializer(ingredients_of_recipe,
                                             many=True).data

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        if request.user is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user.id,
                                       recipe=recipe.id).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        if request.user is None or request.user.is_anonymous:
            return False
        return Cart.objects.filter(user=request.user.id,
                                   recipe=recipe.id).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(default=serializers.CurrentUserDefault())
    ingredients = SetIngredientsToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    name = serializers.CharField()
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientsOfRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        tag_data = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        if validated_data.get('image') is not None:
            image = validated_data.pop('image')
        recipe = Recipe.objects.create(**validated_data)
        recipe.save()
        recipe.image.set(image)
        recipe.tags.set(tag_data)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        IngredientsOfRecipe.objects.filter(recipe=recipe).delete()
        if validated_data.get('image') is not None:
            recipe.image = validated_data.get('image')
        recipe.name = validated_data.get('name')
        recipe.text = validated_data.get('text')
        recipe.cooking_time = validated_data.get('cooking_time')
        recipe.save()
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, recipe):
        return RecipeReadSerializer(recipe,
                                    context={
                                        'request': self.context['request']
                                    }
                                    ).data

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                "Cooking time can't be less than 1 min."
            )
        return cooking_time

    def validate_name(self, name):
        if self.context.get('request').method == 'GET':
            return name
        if Recipe.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                "Recipe with such name already exists."
            )
        return name


class MarkedPreviewRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('recipe', 'user')
            )
        ]

    def to_representation(self, instance):
        return MarkedPreviewRepresentationSerializer(instance.recipe).data


class CartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Cart
        fields = ('user', 'recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('recipe', 'user')
            )
        ]

    def to_representation(self, instance):
        return MarkedPreviewRepresentationSerializer(instance.recipe).data
