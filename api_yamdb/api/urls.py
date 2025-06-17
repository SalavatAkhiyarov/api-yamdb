from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

from .views import UserViewSet

v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/token/', views.TokenView.as_view(), name='token'),
    path('', include(v1_router.urls))
]