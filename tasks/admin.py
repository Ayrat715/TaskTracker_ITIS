from django.contrib import admin
from .models import *


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'keywords', 'processed_keywords')
    readonly_fields = ('processed_keywords',)
    search_fields = ('name', 'keywords')


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('type',)
    list_editable = ('type',)
    list_display_links = None
    ordering = ('id',)


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('type', 'get_weight')
    readonly_fields = ('get_weight',)

    def get_weight(self, obj):
        return obj.get_weight()

    get_weight.short_description = 'Weight'


class SprintAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'start_time', 'end_time')
    list_filter = ('project',)
    raw_id_fields = ('project',)
    date_hierarchy = 'start_time'


class ExecutorInline(admin.TabularInline):
    model = Executor
    extra = 1
    raw_id_fields = ('employee',)


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1
    readonly_fields = ('created_at',)
    raw_id_fields = ('employee',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_number', 'name', 'status', 'priority', 'category',
                    'author', 'predicted_duration')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('name', 'description')
    raw_id_fields = ('author', 'category', 'status', 'priority')
    inlines = [ExecutorInline, CommentInline]
    readonly_fields = ('predicted_duration', 'nlp_metadata')
    actions = ['predict_duration_action']

    def predict_duration_action(self, request, queryset):
        for task in queryset:
            task.predict_duration()

    predict_duration_action.short_description = "Predict duration for selected tasks"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'employee', 'created_at')
    list_filter = ('task', 'employee')
    search_fields = ('title', 'body')
    raw_id_fields = ('task', 'employee')
    readonly_fields = ('created_at',)
