from datetime import datetime
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.validators import RegexValidator
import random

from rest_framework import serializers
from reviews.models import (
    Category,
    Genre,
    Title,
    ReviewModel,
    CommentModel
)

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150, validators=[RegexValidator(r'^[\w.@+-]+$')])

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Username 'me' использовать нельзя")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Такой username уже существует')
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Такой email уже зарегистрирован')
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, validators=[RegexValidator(r'^[\w.@+-]+$')])
    confirmation_code = serializers.CharField(max_length=6)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('Пользователь с таким username не найден')
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError('Неверный код подтверждения')
        return data


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, validators=[RegexValidator(r'^[\w.@+-]+$')])
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'bio')
    
    def update(self, instance, validated_data):
        validated_data['username'] = validated_data.get('username', instance.username)
        validated_data['email'] = validated_data.get('email', instance.email)
        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = ReviewModel
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = CommentModel
        fields = ('id', 'text', 'author', 'pub_date')


# Расчет рейтинга по всем отзывам о Title, добавить в сериализатор Title
# from django.db.models import Avg
#
# class TitleSerializer(serializers.ModelSerializer):
#     rating = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Title
#         fields = ('rating',)
#
#     def get_rating(self, obj):
#         reviews = obj.reviews.all()
#         if not reviews.exists():
#             return 0
#         avg = reviews.aggregate(avg=Avg('score'))['avg']
#         return round(avg)
