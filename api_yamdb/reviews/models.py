from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# User = get_user_model()  # Добавить, , когда появится модель пользователя


class ReviewModel(models.Model):
    text = models.TextField()
    author = models.IntegerField(null=True)
    # author = models.ForeignKey(  # Заменить, когда появится модель пользователя
    #     Users,
    #     on_delete=models.CASCADE,
    #     related_name='reviews'
    # )
    score = models.IntegerField('Оценка')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.text[:25]} ({self.author=})'


class CommentModel(models.Model):
    text = models.TextField()
    author = models.IntegerField(null=True)
    # author = models.ForeignKey(  # Заменить, когда появится модель пользователя
    #     Users,
    #     on_delete=models.CASCADE,
    #     related_name='reviews'
    # )
    review = models.ForeignKey(
        ReviewModel,
        related_name='comments',
        on_delete=models.CASCADE
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.text[:25]} ({self.author=})'


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
    year = models.PositiveSmallIntegerField(
        'Год выпуска',
        db_index=True
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
    rating = models.PositiveSmallIntegerField(
        'Рейтинг',
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')

    def __str__(self):
        return self.name
