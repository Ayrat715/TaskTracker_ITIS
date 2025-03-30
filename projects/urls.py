from django.urls import path

from projects.views import ProjectCreateApiView, ProjectDetailApiView

app_name = "projects"

urlpatterns = [
    path('create/', ProjectCreateApiView.as_view(), name='create'),
    path('<int:pk>/', ProjectDetailApiView.as_view(), name='detail'),
]