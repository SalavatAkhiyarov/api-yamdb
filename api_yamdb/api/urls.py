from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

from .views import (
    UserViewSet,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet
)

v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/token/', views.TokenView.as_view(), name='token'),
    path('', include(v1_router.urls))
]