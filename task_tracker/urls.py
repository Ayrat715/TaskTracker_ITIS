from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('task/', include('tasks.urls')),
    path('account/', include('users.urls')),
    path('project/', include('projects.urls')),
]

