from django.contrib import admin

from .models import ReviewModel, CommentModel


@admin.register(ReviewModel)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(CommentModel)
class GroupAdmin(admin.ModelAdmin):
    pass
