from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from projects.views import ProjectViewSet, ProjectRoleViewSet, EmployeeViewSet

app_name = "projects"

router = DefaultRouter()
router.register('', ProjectViewSet, basename='index')

nested_router = NestedDefaultRouter(router, r'', lookup='project')
nested_router.register('employees', EmployeeViewSet, basename='project-employees')
nested_router.register('roles', ProjectRoleViewSet, basename='project-roles')

urlpatterns = router.urls + nested_router.urls
