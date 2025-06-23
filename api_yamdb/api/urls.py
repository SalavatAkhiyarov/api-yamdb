from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    SignUpView,
    TokenView,
    ReviewViewSet,
    CommentViewSet
)

v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', TokenView.as_view(), name='token'),
    path('v1/', include(v1_router.urls))
]
