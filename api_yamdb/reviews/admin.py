from django.contrib import admin

from .models import Review, Comment, Category, Genre, Title, MyUser


class MyUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'bio')
    search_fields = ('email', 'first_name', 'last_name', 'role')
    list_filter = ('role',)


@admin.register(Review)
class GroupAdmin(admin.ModelAdmin):
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
class GroupAdmin(admin.ModelAdmin):
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
    list_display = ('name', 'year', 'category', 'description')
    search_fields = ('name', 'category__name', 'genre__name')
    list_filter = ('category', 'genre', 'year')


    
admin.site.register(MyUser, MyUserAdmin)

