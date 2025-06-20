from django.contrib import admin

from .models import Review, Comment, Category, Genre, Title


@admin.register(Review)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category', 'description')
    search_fields = ('name', 'category__name', 'genre__name')
    list_filter = ('category', 'genre', 'year')