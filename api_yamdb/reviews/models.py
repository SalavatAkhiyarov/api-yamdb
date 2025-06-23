from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)
from django.core.exceptions import ValidationError

from .validators import validate_year_not_in_future, validate_username
from .constants import (
    USER,
    ADMIN,
    MODERATOR,
    MAX_NAME_FIELD_LENGTH,
    MAX_LENGTH_EMAIL,
    MAX_ROLE_LENGTH,
    STR_LIMIT,
    ROLE_CHOICES
)

ROLE_CHOICES = (
    (USER, 'Аутентифицированный пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор')
)


class User(AbstractUser):
    username = models.CharField(
        'Ник',
        max_length=MAX_NAME_FIELD_LENGTH,
        unique=True,
        validators=(validate_username,)
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        null=False,
        blank=False
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_NAME_FIELD_LENGTH,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_NAME_FIELD_LENGTH,
        null=True,
        blank=True
    )
    bio = models.TextField(
        'Описание',
        null=True,
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=MAX_ROLE_LENGTH,
        blank=True,
        default=USER,
        choices=ROLE_CHOICES
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=6,
        null=True,
        blank=True)

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR
    
    def __str__(self):
        return self.username[:STR_LIMIT]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('role',)


class Category(models.Model):
    name = models.CharField(
        'Название категории',
        max_length=256,
        unique=True
    )
    slug = models.SlugField(
        'Slug категории',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        'Название жанра',
        max_length=256,
        unique=True
    )
    slug = models.SlugField(
        'Slug жанра',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        'Название произведения',
        max_length=256
    )
    year = models.SmallIntegerField(
        'Год выпуска',
        db_index=True,
        validators=[validate_year_not_in_future]
    )
    description = models.TextField(
        'Описание',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        'Оценка',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique-author-title'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.text[:25]} ({self.author=})'


class Comment(models.Model):
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        related_name='comments',
        on_delete=models.CASCADE
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.text[:25]} ({self.author=})'
