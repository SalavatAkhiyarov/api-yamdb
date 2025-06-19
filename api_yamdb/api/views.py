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
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import SignUpSerializer, TokenSerializer, UserSerializer
from .permissions import AdminRole, IsAuthorModeratorAdminOrReadOnly, IsAdminOrReadOnly
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
        username = request.data.get('username')
        email = request.data.get('email')        
        user = User.objects.filter(username=username, email=email).first()
        if user:
            confirmation_code = str(random.randint(100000, 999999))
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
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            confirmation_code = str(random.randint(100000, 999999))
            user = User.objects.create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                confirmation_code=confirmation_code
            )
            user.save()
            send_mail(
                subject='Код подтверждения',
                message=f'Ваш код: {confirmation_code}',
                from_email='from@example.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({'email': user.email, 'username': user.username}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=serializer.validated_data['username'])
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_permissions(self):
        if self.kwargs.get('username') == 'me':
            return [IsAuthenticated()]
        return [AdminRole()]

    def get_object(self):
        if self.kwargs.get('username') == 'me':
            return self.request.user
        return super().get_object()

    def create(self, request, *args, **kwargs):
        username = request.data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError(f"Пользователь с username '{username}' уже существует")
        email = request.data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(f"Пользователь с email '{email}' уже существует")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response({'error': 'Метод PUT не поддерживается'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        user = self.get_object()
        if 'role' in request.data and not request.user.role == 'admin':
            return Response({'error': 'Изменение роли запрещено'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        if self.kwargs.get("username") == "me":
            return Response({'error': 'Удаление своей учетной записи запрещено'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class BaseCategoryGenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAdminOrReadOnly,)
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
    queryset = Title.objects.select_related('category').prefetch_related('genre')
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_queryset(self):
        """Кастомная фильтрация для произведений"""
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
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

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {'error': 'Метод PUT не поддерживается'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)
