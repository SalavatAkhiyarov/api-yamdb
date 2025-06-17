import random

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from django.core.validators import RegexValidator

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
