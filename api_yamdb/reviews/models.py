from django.contrib.auth import get_user_model
from django.db import models

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
