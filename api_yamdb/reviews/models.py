from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)

from .validators import validate_year_not_in_future, validate_username
from .constants import (
    USER,
    ADMIN,
    MODERATOR,
    MAX_NAME_FIELD_LENGTH,
    MAX_LENGTH_EMAIL,
    MAX_ROLE_LENGTH,
    STR_LIMIT,
    ROLE_CHOICES,
    SCORE_MIN_VALUE,
    SCORE_MAX_VALUE,
    MAX_LEN_NAME,
    MAX_LEN_SLUG,
    MAX_LEN_TITLE_NAME,
    MAX_LEN_DESCRIPTION
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


class CategoryGenreBase(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_LEN_NAME,
        unique=True
    )
    slug = models.SlugField(
        'Slug',
        max_length=MAX_LEN_SLUG,
        unique=True
    )

    class Meta:
        abstract = True
        ordering = ('name',)
        verbose_name = 'Базовый класс категории/жанра'
        verbose_name_plural = 'Базовые классы категорий/жанров'

    def __str__(self):
        return self.name[:20]


class Category(CategoryGenreBase):
    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreBase):
    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        'Название произведения',
        max_length=MAX_LEN_TITLE_NAME
    )
    year = models.SmallIntegerField(
        'Год выпуска',
        db_index=True,
        validators=[validate_year_not_in_future]
    )
    description = models.TextField(
        'Описание',
        blank=True,
        null=True,
        max_length=MAX_LEN_DESCRIPTION
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


class ReviewCommentBaseModel(models.Model):
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.text[:25]} ({self.author=})'


class Review(ReviewCommentBaseModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.SmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(SCORE_MIN_VALUE),
            MaxValueValidator(SCORE_MAX_VALUE)
        ]
    )

    class Meta(ReviewCommentBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique-author-title'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(ReviewCommentBaseModel):
    review = models.ForeignKey(
        Review,
        related_name='comments',
        on_delete=models.CASCADE
    )

    class Meta(ReviewCommentBaseModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
