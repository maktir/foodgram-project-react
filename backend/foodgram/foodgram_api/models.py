from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50,
                            unique=True,
                            blank=False,
                            null=False)
    color = models.CharField(max_length=25,
                             unique=True,
                             blank=False,
                             null=False)
    slug = models.SlugField(max_length=200,
                            unique=True,
                            blank=False,
                            null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['slug'],
                name='unique_recipe_tag_slug'
            )
        ]

    def __str__(self):
        return f'{self.slug}'


class TagsOfRecipe(models.Model):
    tag = models.ForeignKey(Tag,
                            related_name='tag_of_recipe',
                            on_delete=models.CASCADE,
                            null=True)
    recipe = models.ForeignKey('Recipe',
                               related_name='tag_of_recipe',
                               on_delete=models.CASCADE,
                               null=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            blank=False,
                            null=False)
    measurement_unit = models.CharField(max_length=50,
                                        blank=False,
                                        null=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.name}'


class IngredientsOfRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   related_name='ingredients_of_recipe',
                                   on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe',
                               related_name='ingredients_of_recipe',
                               on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()


class Recipe(models.Model):
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipe',
                               blank=False,
                               null=False)
    name = models.CharField(max_length=200,
                            blank=False,
                            null=False)
    image = models.ImageField(upload_to='/foodgram/',
                              blank=False,
                              null=False)
    text = models.CharField(max_length=500,
                            blank=False,
                            null=False)
    ingredients = models.ManyToManyField(Ingredient,
                                         through=IngredientsOfRecipe,
                                         related_name='ingredients')
    cooking_time = models.PositiveSmallIntegerField(blank=False,
                                                    null=False)
    tags = models.ManyToManyField(Tag,
                                  through=TagsOfRecipe,
                                  related_name='tags')
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.name}'


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             related_name='favorites',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               related_name='favorites',
                               on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]


class Cart(models.Model):
    user = models.ForeignKey(User,
                             related_name='carted',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               related_name='carted',
                               on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_recipe'
            )
        ]
