from rest_framework.routers import DefaultRouter

from projects.views import ProjectViewSet, ProjectRoleViewSet, EmployeeViewSet

app_name = "projects"

router = DefaultRouter()
router.register('roles', ProjectRoleViewSet, basename='roles')
router.register('employees', EmployeeViewSet, basename='employees')
router.register('', ProjectViewSet, basename='index')

urlpatterns = router.urls
