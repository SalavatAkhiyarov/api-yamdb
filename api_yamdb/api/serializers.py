
import random

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from django.core.validators import RegexValidator
from datetime import datetime

from rest_framework import serializers
from reviews.models import Category, Genre, Title

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
