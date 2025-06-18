from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import UserViewSet
from reviews.views import ReviewViewSet, CommentViewSet

v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
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
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/token/', views.TokenView.as_view(), name='token'),
    path('', include(v1_router.urls))
]