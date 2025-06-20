from django.contrib import admin

from .models import Review, Comment


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
