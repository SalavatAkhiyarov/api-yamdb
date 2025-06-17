from rest_framework import serializers

from .models import ReviewModel, CommentModel


class ReviewSerializer(serializers.ModelSerializer):
    # author = SlugRelatedField(slug_field='username', read_only=True)
    # Добавить, когда появится модель пользователя.

    class Meta:
        model = ReviewModel
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    # author = SlugRelatedField(slug_field='username', read_only=True)
    # Добавить, когда появится модель пользователя.

    class Meta:
        model = ReviewModel
        fields = ('id', 'text', 'author', 'pub_date')
