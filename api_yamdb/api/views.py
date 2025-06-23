import random

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.exceptions import ValidationError
from rest_framework import filters

from .permissions import (
    AdminRole,
    IsAdminOrReadOnly,
    IsAuthorModeratorAdminOrReadOnly
)
from reviews.models import (
    Category,
    Genre,
    Title,
    Review
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
    ReviewSerializer,
    CommentSerializer
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
            user, created = User.objects.get_or_create(
                username=username,
                email=email
            )
            if not created:
                user.confirmation_code = confirmation_code
                user.save()
            user.confirmation_code = confirmation_code
            user.save()
            send_mail(
                subject='Код подтверждения',
                message=f'Ваш код: {confirmation_code}',
                from_email='from@example.com',
                recipient_list=[email],
                fail_silently=False,
            )
            return Response(
                {'email': email, 'username': username},
                status=status.HTTP_200_OK
            )
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
            return Response(
                {'email': user.email, 'username': user.username},
                status=status.HTTP_200_OK
            )
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
    lookup_field = 'username'
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
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                f"Пользователь с username '{username}' уже существует"
            )
        email = request.data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(
                f"Пользователь с email '{email}' уже существует"
            )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {'error': 'Метод PUT не поддерживается'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        user = self.get_object()
        data = request.data.copy()
        if self.kwargs.get('username') == 'me':
            if 'role' in data:
                data.pop('role')
        elif 'role' in data and not (
            request.user.is_superuser or request.user.role == 'admin'
        ):
            data.pop('role')
        serializer = self.get_serializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if self.kwargs.get('username') == 'me':
            return Response(
                {'error': 'Удаление своей учетной записи запрещено'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
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
    queryset = (
        Title.objects
        .select_related('category')
        .prefetch_related('genre')
        .annotate(rating=Avg('reviews__score'))
    )
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    http_method_names = ['get', 'post', 'patch', 'delete']

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
        return queryset.distinct().order_by('-year', 'name')

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от типа запроса"""
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorModeratorAdminOrReadOnly,
    )
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorModeratorAdminOrReadOnly,
    )
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title=self.get_title(),
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
