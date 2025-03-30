from rest_framework import permissions


class ProjectPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated and
                request.user in obj.group.user_set.all())
