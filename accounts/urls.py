from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    
    # Admin-only URLs
    path('user-management/', views.user_management_view, name='user_management'),
    path('delete-user/<int:user_id>/', views.delete_user_view, name='delete_user'),
    path('admin/edit-user/<int:user_id>/', views.edit_user_admin_view, name='edit_user_admin'),
]