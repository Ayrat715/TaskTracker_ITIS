from django.urls import path

from projects.views import ProjectCreateApiView, ProjectDetailApiView, \
    UserProjectListViewSet, ProjectEmployeesView, MyEmployeeIdView

app_name = "projects"

urlpatterns = [
    path('create/', ProjectCreateApiView.as_view(), name='create'),
    path(
        'list/',
        UserProjectListViewSet.as_view(),
        name='user-projects'
    ),
    path('<int:pk>/', ProjectDetailApiView.as_view(), name='detail'),
    path('<int:project_id>/employees/', ProjectEmployeesView.as_view(), name='project-employees'),
    path('my-employee-ids/', MyEmployeeIdView.as_view(), name='my-employee-ids'),
]