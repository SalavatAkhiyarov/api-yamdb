from django_filters import rest_framework as filters

from reviews.models import Title


class TitleFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text='Поиск по названию произведения'
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='exact',
        help_text='Фильтрация по slug жанра'
    )
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact',
        help_text='Фильтрация по slug категории'
    )

    class Meta:
        model = Title
        fields = ('name', 'genre', 'category', 'year')
