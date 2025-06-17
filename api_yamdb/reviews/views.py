from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import ReviewModel, CommentModel
from api.models import TitleModel
from .permissions import IsAuthorModeratorAdminOrReadOnly
from .serializers import ReviewSerializer, CommentSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = ReviewModel.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (
        IsAuthenticated,
        IsAuthorModeratorAdminOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(TitleModel, pk=self.kwargs['title_id'])
        return title.reviews.all()
    # У модели TitleModel, если она так называется,
    # должно быть указано related_name='reviews'

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)
    # Добавить, когда появится модель пользователя.


class CommentViewSet(viewsets.ModelViewSet):
    queryset = CommentModel.objects.all()
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
            review=review
        )
    # author=self.request.user
    # Добавить, когда появится модель пользователя.
