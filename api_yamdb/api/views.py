
import random

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny

from .serializers import SignUpSerializer, TokenSerializer, UserSerializer
from .permissions import AdminRole

User = get_user_model()


class SignUpView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            confirmation_code = str(random.randint(100000, 999999))
            user, created = User.objects.get_or_create(username=username, email=email)
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