import random

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken
from django.core.validators import RegexValidator

from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment
)
from reviews.constants import (
    MAX_NAME_FIELD_LENGTH,
    MAX_LENGTH_EMAIL
)
from .validators import UsernameValidationMixin

User = get_user_model()


class SignUpSerializer(serializers.Serializer, UsernameValidationMixin):
    email = serializers.EmailField(max_length=MAX_LENGTH_EMAIL)
    username = serializers.CharField(max_length=MAX_NAME_FIELD_LENGTH)

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        confirmation_code = str(random.randint(100000, 999999))
        user = User.objects.filter(username=username, email=email).first()
        if user:
            user.confirmation_code = confirmation_code
            user.save()
        else:
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError(
                    'Username уже используется другим пользователем'
                )
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    'Email уже используется другим пользователем'
                )
            user = User.objects.create(
                username=username,
                email=email,
                confirmation_code=confirmation_code
            )
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=MAX_NAME_FIELD_LENGTH,
        validators=[
            RegexValidator(
                r'^[\w.@+-]+$',
                message=(
                    'Имя пользователя может содержать только буквы, '
                    'цифры и символы @/./+/-/_'
                )
            )
        ]
    )
    confirmation_code = serializers.CharField(max_length=6)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not user.confirmation_code:
            raise serializers.ValidationError(
                'Код уже был использован или не запрошен'
            )
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError('Неверный код подтверждения')
        user.confirmation_code = ''
        user.save()
        token = AccessToken.for_user(user)
        return {'token': str(token)}


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'role', 'bio'
        )

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            username = data.get('username')
            email = data.get('email')
            if User.objects.filter(username=username).exists():
                raise ValidationError(
                    f"Пользователь с username '{username}' уже существует"
                )
            if email and User.objects.filter(email=email).exists():
                raise ValidationError(
                    f"Пользователь с email '{email}' уже существует"
                )
        return data


class UserMeSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


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
    rating = serializers.IntegerField()

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
        many=True,
        allow_empty=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def title_read(self, instance):
        return TitleReadSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        required=False,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)

    def validate(self, data):
        if self.instance:
            return data

        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user

        if Review.objects.filter(title_id=title_id, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение.'
            )

        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
