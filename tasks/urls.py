from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import SprintViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'sprints', SprintViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
