from django.db import models
from django.contrib.auth.models import AbstractUser

ROLE_CHOICES = (
    ('user', 'Аутентифицированный пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
)


class MyUser(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField('first_name', max_length=150, null=True, blank=True)
    last_name = models.CharField('last_name', max_length=150, null=True, blank=True)
    bio = models.TextField('Био', null=True, blank=True)
    role = models.CharField('Роль', max_length=10, blank=True, default='user', choices=ROLE_CHOICES)
    confirmation_code = models.CharField(max_length=20, null=True, blank=True)
