from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from .forms import (
    UserLoginForm, UserRegistrationForm, UserPasswordChangeForm, 
    UserPasswordResetForm, UserSetPasswordForm, UserUpdateForm,
    FarmerProfileForm, CustomerProfileForm, DeliveryPersonnelProfileForm, 
    MillOperatorProfileForm, AdminProfileForm
)
from .models import CustomUser, Farmer

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from django.db.models import Count


def landing_page(request):
    return render(request, 'core/landing_page.html')


# User Login View
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful.")
            
            # Redirect based on user role
            if user.role == CustomUser.Role.ADMIN:
                return redirect('admin_dashboard')
            elif user.role == CustomUser.Role.FARMER:
                return redirect('farmer_dashboard')
            elif user.role == CustomUser.Role.CUSTOMER:
                return redirect('customer_dashboard')
            elif user.role == CustomUser.Role.DELIVERY:
                return redirect('delivery_dashboard')
            elif user.role == CustomUser.Role.MILL_OPERATOR:
                return redirect('mill_operator_dashboard')
            else:
                return redirect('dashboard')  # Fallback for undefined roles
    else:
        form = UserLoginForm()
    return render(request, 'core/auth/login.html', {'form': form})


# User Logout View
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

# Registration Views (Only Admin, Farmers, and Customers can self-register)
def register_admin(request):
    if not request.user.is_superuser:
        messages.error(request, "Only superusers can register new admins.")
        return redirect('dashboard')
    return handle_registration(request, CustomUser.Role.ADMIN, 'core/auth/register_admin.html')

def register_farmer(request):
    return handle_registration(request, CustomUser.Role.FARMER, 'core/auth/register_farmer.html')

def register_customer(request):
    return handle_registration(request, CustomUser.Role.CUSTOMER, 'core/auth/register_customer.html')

# Helper function for registration
def handle_registration(request, role, template):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = role
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
    else:
        form = UserRegistrationForm(user=request.user)
    return render(request, template, {'form': form})

# Profile Update View
@login_required
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        profile_form = get_profile_form(user)(request.POST, instance=user.get_profile())
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')  # Redirect to profile view instead
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = get_profile_form(user)(instance=user.get_profile())
    
    return render(request, 'core/auth/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# Password Change View
@login_required
def change_password(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Password changed successfully.")
            return redirect('profile')
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request, 'core/auth/password_change.html', {'form': form})

# Password Reset Views
def password_reset_request(request):
    if request.method == 'POST':
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            messages.success(request, "Password reset email sent.")
            return redirect('login')
    else:
        form = UserPasswordResetForm()
    return render(request, 'core/auth/password_reset.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    form = UserSetPasswordForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Password reset successful. You can now log in.")
        return redirect('login')
    return render(request, 'core/auth/password_reset_confirm.html', {'form': form})


# dashboards===================================
@login_required
def admin_dashboard(request):
    # Check if the user is an admin
    if request.user.role != CustomUser.Role.ADMIN:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')

    # Fetch the total number of users and total number of users with the FARMER role
    total_users = CustomUser.objects.count()
    total_farmers = CustomUser.objects.filter(role=CustomUser.Role.FARMER).count()  # Count users with role FARMER

    # Pass the data to the template
    return render(request, 'core/dashboards/admin_dashboard.html', {
        'total_users': total_users,
        'total_farmers': total_farmers,
    })



@login_required
def farmer_dashboard(request):
    if request.user.role != CustomUser.Role.FARMER:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    return render(request, 'core/dashboards/farmer_dashboard.html')

@login_required
def customer_dashboard(request):
    if request.user.role != CustomUser.Role.CUSTOMER:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    return render(request, 'core/dashboards/customer_dashboard.html')

@login_required
def delivery_dashboard(request):
    if request.user.role != CustomUser.Role.DELIVERY:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    return render(request, 'core/dashboards/delivery_dashboard.html')

@login_required
def mill_operator_dashboard(request):
    if request.user.role != CustomUser.Role.MILL_OPERATOR:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    return render(request, 'core/dashboards/mill_operator_dashboard.html')





# Utility function to get the correct profile form
def get_profile_form(user):
    if user.role == CustomUser.Role.FARMER:
        return FarmerProfileForm
    elif user.role == CustomUser.Role.CUSTOMER:
        return CustomerProfileForm
    elif user.role == CustomUser.Role.DELIVERY:
        return DeliveryPersonnelProfileForm
    elif user.role == CustomUser.Role.MILL_OPERATOR:
        return MillOperatorProfileForm
    elif user.role == CustomUser.Role.ADMIN:
        return AdminProfileForm
    return None



@login_required
def profile_view(request):
    """
    Main profile view that shows the user's profile information
    """
    user = request.user
    profile = user.get_profile()  # This assumes you have a get_profile() method in your CustomUser model
    
    context = {
        'user': user,
        'profile': profile,
    }
    
    return render(request, 'core/auth/profile.html', context)


# for admin only-----------------------------------------------
# Function to check if the user is an admin
def is_admin(user):
    return user.is_authenticated and user.role == CustomUser.Role.ADMIN

# 🔹 View: List all users
class UserListView(ListView):
    model = CustomUser
    template_name = 'core/dashboards/admin/users/user_list.html'  # Updated path
    context_object_name = 'users'

    def get_queryset(self):
        return CustomUser.objects.all()

# 🔹 View: Create a new user (Admin Only)
class UserCreateView(CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'core/dashboards/admin/users/user_form.html'  # Updated path
    success_url = reverse_lazy('admin-user-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "User added successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error creating user. Please check the form.")
        return super().form_invalid(form)

# 🔹 View: Update an existing user
class UserUpdateView(UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'core/dashboards/admin/users/user_form.html'  # Updated path
    success_url = reverse_lazy('admin-user-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "User updated successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error updating user.")
        return super().form_invalid(form)

# 🔹 View: Delete a user
class UserDeleteView(DeleteView):
    model = CustomUser
    template_name = 'core/dashboards/admin/users/user_confirm_delete.html'  # Updated path
    success_url = reverse_lazy('admin-user-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "User deleted successfully!")
        return super().delete(request, *args, **kwargs)
