from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import SprintViewSet, TaskViewSet, StatusListView, PriorityListView

router = DefaultRouter()
router.register(r'sprints', SprintViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('statuses/', StatusListView.as_view(), name='status-list'),
    path('priorities/', PriorityListView.as_view(), name='priority-list'),
]
