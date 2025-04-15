from django.contrib.auth.models import Group
from rest_framework import permissions


class UserPermitions(permissions.BasePermission):
    """
    Класс реализующий собственную проверку на то, что пользователь принадлежит
    группе.
    """

    def has_object_permission(self, request, view, obj: Group) -> bool:
        """
        Определение доступа к модели группы.

        :param request: данные запроса.
        :param view: вид.
        :param obj: экземпляр группы.
        :return: bool True - пользователь принадлежит группе, False - в
        противном случае.
        """

        return (
                request.user.is_authenticated and
                request.user.groups.filter(id=obj.id).exists()
        )
