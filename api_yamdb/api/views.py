
import random

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, filters, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny

from .serializers import SignUpSerializer, TokenSerializer, UserSerializer
from .permissions import AdminRole
from reviews.models import Category, Genre, Title
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer
)


User = get_user_model()


class SignUpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            confirmation_code = str(random.randint(100000, 999999))
            user, created = User.objects.get_or_create(username=username,email=email)
            if not created:
                user.confirmation_code = confirmation_code
                user.save()
            send_mail(
                subject='Код подтверждения',
                message=f'Ваш код: {confirmation_code}',
                from_email='from@example.com',
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({'email': email, 'username': username}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, username=serializer.validated_data['username'])
            if user.confirmation_code != serializer.validated_data['confirmation_code']:
                return Response({'error': 'Неверный код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (AdminRole,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        if 'username' not in request.data:
            request.data['username'] = user.username
        if 'email' not in request.data:
            request.data['email'] = user.email
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseCategoryGenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (AdminRole,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(BaseCategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (AdminRole,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_queryset(self):
        """Кастомная фильтрация для произведений"""
        queryset = super().get_queryset()
        genre_slug = self.request.query_params.get('genre')
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        year = self.request.query_params.get('year')
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(year=year)
            except ValueError:
                raise ValidationError(
                    {'year': 'year должен быть целым числом'}
                )
        return queryset.distinct()

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от типа запроса"""
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitleWriteSerializer
