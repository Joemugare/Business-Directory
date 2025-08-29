from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.user_register, name='register'),  # Fixed from views.register
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('profile/', views.user_profile, name='profile'),  # Ensure this exists
]