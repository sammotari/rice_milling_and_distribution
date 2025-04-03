from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    user_login, user_logout, register_admin, register_farmer, register_customer,
    update_profile, change_password, admin_dashboard, farmer_dashboard, customer_dashboard,
    delivery_dashboard, mill_operator_dashboard,
    UserListView, UserCreateView, UserUpdateView, UserDeleteView,
)
from . import views

urlpatterns = [
    # Landing Page
    path('', views.landing_page, name='landing_page'),

    # Authentication URLs
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    # Registration URLs
    path('register/admin/', register_admin, name='register_admin'),
    path('register/farmer/', register_farmer, name='register_farmer'),
    path('register/customer/', register_customer, name='register_customer'),

    # Profile & Account Management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', update_profile, name='update_profile'),
    path('profile/change-password/', change_password, name='change_password'),

    # Password Reset URLs
    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # Dashboard URLs
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/farmer/', farmer_dashboard, name='farmer_dashboard'),
    path('dashboard/customer/', customer_dashboard, name='customer_dashboard'),
    path('dashboard/delivery/', delivery_dashboard, name='delivery_dashboard'),
    path('dashboard/mill-operator/', mill_operator_dashboard, name='mill_operator_dashboard'),

    # Custom Admin URLs (Admin Only) - Updated to avoid conflict
    path('custom-admin/users/', UserListView.as_view(), name='admin-user-list'),      # View all users
    path('custom-admin/users/add/', UserCreateView.as_view(), name='admin-user-create'), # Add a new user
    path('custom-admin/users/edit/<uuid:pk>/', UserUpdateView.as_view(), name='admin-user-edit'),
    path('custom-admin/users/delete/<uuid:pk>/', UserDeleteView.as_view(), name='admin-user-delete'),
]
