from django.contrib import admin

from .models import Review, Comment


@admin.register(Review)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class GroupAdmin(admin.ModelAdmin):
    pass
