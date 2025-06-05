from django.contrib.auth.views import LogoutView
from django.urls import path, include
from rest_framework import routers

from users import views
from users.views import GroupViewSet, UserDetailView

app_name = 'users'

router = routers.DefaultRouter()
router.register(r'groups', GroupViewSet, basename='group')

urlpatterns = [
    path('registration-user/', views.UserRegistrationView.as_view(), name='registration_user'),
    path('login-user/', views.UserLoginView.as_view(), name='login_user'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('user/', views.UserStatus.as_view(), name='user_status'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
    path('users/<int:id>/', UserDetailView.as_view(), name='user-detail'),
]