from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.contrib.auth import get_user_model
from .models import Follow


from foodgram_api.models import Recipe


User = get_user_model()


class RegistrySerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[
        UniqueValidator(queryset=User.objects.all())])
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(required=True, validators=[
        UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True,
                                     write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user__id=request.user.id, author__id=author.id).exists()


class MarkedPreviewRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionListSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='author.email')
    id = serializers.PrimaryKeyRelatedField(source='author.id',
                                            queryset=User.objects.all())
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = MarkedPreviewRepresentationSerializer(many=True,
                                                    source='author.recipe')
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'username', 'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        try:
            user = self.context['request'].user
            if not user.is_anonymous:
                return user.follower.filter(author=obj.author.id).exists()
            else:
                return False
        except KeyError:
            return False

    def get_recipes_count(self, obj):
        return obj.author.recipe.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]

    def validate_author(self, author):
        if author == self.context['request'].user:
            raise serializers.ValidationError(
                "You can't subscribe to yourself!")
        return author

    def to_representation(self, instance):
        return SubscriptionListSerializer(instance).data
