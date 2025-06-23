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
auth_urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='token'),
]
v1_urlpatterns = [
    path('auth/', include((auth_urlpatterns, 'auth'))),
    *v1_router.urls
]

urlpatterns = [
    path('v1/', include((v1_urlpatterns, 'v1'))),
]
