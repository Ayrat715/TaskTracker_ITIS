from rest_framework import permissions

from projects.models import Employee


class IsEmployeeOfProject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return Employee.objects.filter(project=obj, user=request.user).exists()

    def has_permission(self, request, view):
        project_id = request.data.get('project') or request.query_params.get('project')
        if project_id:
            return Employee.objects.filter(
                user=request.user,
                project__id=project_id
            ).exists()
        return True


class IsEmployeeOfProjectRole(IsEmployeeOfProject):
    def has_object_permission(self, request, view, obj):
        return Employee.objects.filter(project=obj.project,
                                       user=request.user).exists()

class IsEmployee(IsEmployeeOfProject):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
