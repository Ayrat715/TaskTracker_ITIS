from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path('registration-user/', views.UserRegistrationView.as_view(), name='registration_user'),
    path('login-user/', views.UserLoginView.as_view(), name='login_user'),
]