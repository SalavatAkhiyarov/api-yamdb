from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import Title, ReviewModel, CommentModel
from api.serializers import ReviewSerializer, CommentSerializer
from api.permissions import IsAuthorModeratorAdminOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (
        IsAuthenticated,
        IsAuthorModeratorAdminOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (
        IsAuthenticated,
        IsAuthorModeratorAdminOrReadOnly,
    )

    def get_queryset(self):
        review = get_object_or_404(ReviewModel, pk=self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(ReviewModel, pk=self.kwargs['review_id'])
        serializer.save(
            author=self.request.user,
            review=review
        )
