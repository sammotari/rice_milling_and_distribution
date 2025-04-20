from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    paddy_supply_list_view, set_paddy_price, user_login, user_logout, register_admin, register_farmer, register_customer,
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
    path('profile/edit/', views.update_profile, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),



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

    # paddy price
    path('set-paddy-price/', set_paddy_price, name='set-paddy-price'),
    path('success/', views.success_view, name='success_url'),  # Add this URL
    
    path('supply/record/', views.record_supply_view, name='record_supply'),
    path('supply/<uuid:supply_id>/approve/', views.approve_payment_view, name='approve_payment'),
    path('supply/list/', paddy_supply_list_view, name='supply_list'),

    # paddy inventory
    path('inventory/', views.inventory_view, name='inventory_view'),
    # Mill operator view for processing rice
    path('process-rice/', views.process_rice_view, name='process_rice'),
    # Success page for processing rice
    path('processed-rice-success/', views.processed_rice_success, name='processed_rice_success'),



    path('packages/', views.package_list, name='package_list'),
    path('packages/create/', views.package_create, name='package_create'),
    path('packages/<int:pk>/edit/', views.package_update, name='package_update'),
    path('packages/<int:pk>/delete/', views.package_delete, name='package_delete'),

    



    path('place_order/', views.place_order_view, name='place_order'),
    path('order_list/', views.order_list, name='order_list'),
    path('order_details/<int:order_id>/', views.order_details, name='order_details'),
    path('enter_transaction_code/<int:order_id>/', views.enter_transaction_code, name='enter_transaction_code'),
    path('track_delivery/<int:order_id>/', views.track_delivery, name='track_delivery'),
    # path('confirm_delivery/<int:order_id>/', views.confirm_delivery, name='confirm_delivery'),

    # Admin actions
    path('c-admin/confirm-transaction/<int:transaction_id>/', views.confirm_transaction, name='confirm_transaction'),
    path('c-admin/all-transactions/', views.all_transactions, name='all_transactions'),

    path('c-admin/assign-delivery/', views.assign_delivery, name='assign_delivery'),

    path('c-admin/admin-order-list/', views.admin_order_list, name='admin_order_list'),

    path('delivery/update/<int:order_id>/', views.update_delivery_status, name='update_delivery_status'),



    path('c-admin/orders/<int:pk>/ajax/', views.admin_order_detail_ajax, name='admin_order_detail_ajax'),

    # # order>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # path('place_order/', views.place_order, name='place_order'),  # View for placing an order
    # path('order_list/', views.order_list, name='order_list'),  # View for listing all customer orders
    # path('enter_transaction_code/<int:order_id>/', views.enter_transaction_code, name='enter_transaction_code'),  # View for entering transaction codes
    # path('order_details/<int:order_id>/', views.order_details, name='order_details'),  # View for order details
    # path('track_delivery/<int:order_id>/', views.track_delivery, name='track_delivery'),  # View for tracking delivery
    # path('confirm_delivery/<int:order_id>/', views.confirm_delivery, name='confirm_delivery'),  # Admin view for confirming delivery




]
