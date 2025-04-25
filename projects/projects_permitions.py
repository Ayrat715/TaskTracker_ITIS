from rest_framework import permissions

from projects.models import Employee


class IsEmployeeOfProject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated and
                Employee.objects.filter(project=obj, user=request.user).exists())

    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsEmployeeOfProjectRole(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated and
                Employee.objects.filter(project=obj.project,
                                        user=request.user).exists())

    def has_permission(self, request, view):
        return request.user.is_authenticated and Employee.objects.filter(project=view.kwargs.get('project_pk'), user=request.user).exists()


class IsEmployee(IsEmployeeOfProject):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and Employee.objects.filter(project=obj.project, user=request.user).exists()

    def has_permission(self, request, view):
        project_id = view.kwargs.get('project_pk')
        return request.user.is_authenticated and Employee.objects.filter(project=project_id, user=request.user).exists()
