from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group as AuthGroup
from .models import *

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active',
                                    'is_staff', 'is_superuser', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups',)

admin.site.unregister(AuthGroup)
admin.site.register(User, UserAdmin)

@admin.register(AuthGroup)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_count')
    filter_horizontal = ('permissions',)

    def user_count(self, obj):
        return obj.user_set.count()

    user_count.short_description = 'Users'
