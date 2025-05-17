from django.contrib import admin
from .models import *


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'group')
    list_filter = ('group',)
    raw_id_fields = ('group',)
    date_hierarchy = 'start_time'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'current_load')
    list_filter = ('project', 'role')
    raw_id_fields = ('user', 'project', 'role')
    readonly_fields = ('current_load', 'completed_tasks_count', 'average_completion_time')


@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'project')
    list_filter = ('project',)
    raw_id_fields = ('project',)
