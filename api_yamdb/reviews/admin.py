from django.contrib import admin
from .models import MyUser


class MyUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'bio')
    search_fields = ('email', 'first_name', 'last_name', 'role')
    list_filter = ('role',)


admin.site.register(MyUser, MyUserAdmin)
