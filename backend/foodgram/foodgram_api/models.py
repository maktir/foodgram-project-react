from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Value, Exists, OuterRef

User = get_user_model()


class RecipeQuerySet(models.QuerySet):

    def additional_properties(self, user):
        if user.is_anonymous:
            return self.annotate(is_favorited=Value(
                False, output_field=models.BooleanField()
            ),
                is_in_shopping_cart=Value(
                    False, output_field=models.BooleanField()
                )
            )
        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user=user, recipe__pk=OuterRef('pk')
                )
            ),
            is_in_shopping_cart=Exists(
                Cart.objects.filter(
                    user=user, recipe__pk=OuterRef('pk')
                )
            )
        )


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
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
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

    class Meta:
        verbose_name = 'Tag of recipe'
        verbose_name_plural = 'Tags of recipe'

    def __str__(self):
        return self.pk


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            blank=False,
                            null=False)
    measurement_unit = models.CharField(max_length=50,
                                        blank=False,
                                        null=False)

    class Meta:
        ordering = ['id']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

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

    def __str__(self):
        return self.pk


class Recipe(models.Model):
    pub_date = models.DateTimeField(auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipe',
                               blank=False,
                               null=False)
    name = models.CharField(max_length=200,
                            blank=False,
                            null=False)
    image = models.ImageField(upload_to='foodgram/',
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
    slug = models.SlugField(unique=True,
                            null=True,
                            blank=True)
    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

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
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
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
        verbose_name = 'Carted recipe'
        verbose_name_plural = 'Carted recipes'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_recipe'
            )
        ]
