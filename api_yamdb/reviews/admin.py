from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Review, Comment, Category, Genre, Title, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'role', 'bio'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role',)
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role', 'bio', 'confirmation_code')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'title',
        'score',
        'pub_date',
    )
    search_fields = (
        'author',
        'title',
    )
    list_filter = (
        'author',
        'title',
        'score',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'review',
        'pub_date',
    )
    search_fields = (
        'author',
    )
    list_filter = (
        'review',
    )


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
    list_display = ('name', 'year', 'category', 'display_genres',
                    'description')
    search_fields = ('name', 'category__name', 'genre__name')
    list_filter = ('category', 'genre', 'year')

    @admin.display(description='Жанры')
    def display_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genre.all()])
