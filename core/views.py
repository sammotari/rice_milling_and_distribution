from datetime import datetime, timezone
from decimal import Decimal
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import (
    AdminPaddyPaymentApprovalForm, AssignDeliveryForm, DeliveryUpdateForm, MillOperatorPaddySupplyForm, PackageSizeForm, PaddyPriceForm, PaddySupplyForm, ProcessedRiceForm, UserLoginForm, UserRegistrationForm, UserPasswordChangeForm, 
    UserPasswordResetForm, UserSetPasswordForm, UserUpdateForm,
    FarmerProfileForm, CustomerProfileForm, DeliveryPersonnelProfileForm, 
    MillOperatorProfileForm, AdminProfileForm
)
from .models import CustomUser, Customer, Delivery, DeliveryPersonnel, Farmer, Order, OrderItem, PackageSize, PaddyInventory, PaddyPrice, PaddySupply, ProcessedRiceInventory, SoldRiceInventory, Transaction, User

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from django.db.models import Count
from dal import autocomplete
from django.contrib.auth import get_user_model


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



# Password Change View
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Prevent session logout
            messages.success(request, "Your password was successfully updated!")
            return redirect('profile')  # Redirect to profile view
    else:
        form = PasswordChangeForm(request.user)
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

# Helper function to fetch the latest Paddy Price
def get_latest_paddy_price():
    try:
        return PaddyPrice.objects.latest('effective_date')
    except PaddyPrice.DoesNotExist:
        return None
    

@login_required
def admin_dashboard(request):
    # Check if the user is an admin
    if request.user.role != CustomUser.Role.ADMIN:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    
    # Fetch the necessary data for the dashboard
    total_users = CustomUser.objects.count()
    total_farmers = CustomUser.objects.filter(role=CustomUser.Role.FARMER).count()
    pending_approvals = CustomUser.objects.filter(is_active=False).count()  # Assuming inactive users are pending approval
    todays_orders = Order.objects.filter(created_at__date=datetime.today().date()).count()
    
    # Get the latest Paddy price
    paddy_price = get_latest_paddy_price()
    
    # Render the admin dashboard template
    return render(request, 'core/dashboards/admin_dashboard.html', {
        'total_users': total_users,
        'total_farmers': total_farmers,
        'pending_approvals': pending_approvals,
        'todays_orders': todays_orders,
        'paddy_price': paddy_price,
    })



# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Farmer Dashboard View
@login_required
def farmer_dashboard(request):
    if request.user.role != CustomUser.Role.FARMER:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    
    # Fetch the latest paddy price
    paddy_price = PaddyPrice.objects.order_by('-effective_date').first()

    if not paddy_price:
        messages.error(request, "No paddy price available. Please contact the administrator.")
        return redirect('home')  # Or any other fallback page if no price is available
    
    # Fetch the current farmer's paddy supplies, ordered by most recent first
    paddy_supplies = PaddySupply.objects.filter(farmer=request.user.farmer).order_by('-timestamp')[:5]  # Get the 5 most recent

    # Calculate total supplied paddy
    total_supplied = sum([supply.quantity for supply in paddy_supplies])

    # Calculate total payments (only those that are paid)
    total_payments = sum([supply.total_amount for supply in paddy_supplies if supply.payment_status == 'paid'])

    # Prepare the context to pass to the template
    context = {
        'paddy_supplies': paddy_supplies,
        'total_supplied': total_supplied,
        'paddy_price': paddy_price,
        'total_payments': total_payments,  # Include total payments
    }

    return render(request, 'core/dashboards/farmer_dashboard.html', context)




from django.db.models import Case, When, Value, IntegerField

@login_required
def customer_dashboard(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        return render(request, 'core/dashboards/customer_dashboard.html', {
            'error': 'Customer profile not found.',
        })

    # Annotate orders to prioritize 'paid' first, then sort by created_at
    orders = Order.objects.filter(customer=customer).annotate(
        paid_priority=Case(
            When(status='paid', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('-paid_priority', '-created_at')

    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    paid_orders = orders.filter(status='paid').count()
    delivered_orders = orders.filter(status='delivered').count()

    context = {
        'orders': orders[:5],  # Limit to 5 after ordering
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'paid_orders': paid_orders,
        'delivered_orders': delivered_orders,
    }

    return render(request, 'core/dashboards/customer_dashboard.html', context)



# Delivery Dashboard View
@login_required
def delivery_dashboard(request):
    if request.user.role != CustomUser.Role.DELIVERY:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')

    # Fetch the latest paddy price
    paddy_price = get_latest_paddy_price()

    # Get the logged-in user's delivery personnel instance
    delivery_personnel = DeliveryPersonnel.objects.get(user=request.user)

    # Get assigned orders that are not yet delivered or cancelled
    assigned_orders = Order.objects.filter(
        delivery_personnel=delivery_personnel,
        status__in=['pending', 'paid']  # Only include orders that are not yet delivered or cancelled
    )

    return render(request, 'core/dashboards/delivery_dashboard.html', {
        'assigned_orders': assigned_orders,
        'paddy_price': paddy_price,
        'delivery_personnel': delivery_personnel  # Pass vehicle_number to the template
    })


# Mill Operator Dashboard View
@login_required
def mill_operator_dashboard(request):
    if request.user.role != CustomUser.Role.MILL_OPERATOR:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    
    paddy_price = get_latest_paddy_price()  # Get the latest paddy price
    return render(request, 'core/dashboards/mill_operator_dashboard.html', {'paddy_price': paddy_price})





@login_required
def profile_view(request):
    user = request.user
    profile_instance = user.get_profile()

    # Check if the profile edit form was submitted
    if request.method == "POST":
        # Determine the correct form class based on the user role
        profile_form_class = get_profile_form(user)
        profile_form = profile_form_class(request.POST, instance=profile_instance)

        # If form is valid, save it and redirect back to the profile page
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')

    else:
        # Initialize the profile form for GET request
        profile_form_class = get_profile_form(user)
        profile_form = profile_form_class(instance=profile_instance)

    # Render profile data along with the user-specific profile form
    return render(request, 'core/auth/profile_view.html', {
        'user': user,
        'profile_instance': profile_instance,
        'profile_form': profile_form,
    })


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
def update_profile(request):
    user = request.user
    profile_instance = user.get_profile()  # Assuming this method gives the profile related to the user
    profile_form_class = get_profile_form(user)

    if request.method == 'POST':
        # Handle user and profile form submission
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = profile_form_class(request.POST, instance=profile_instance)

        if user_form.is_valid() and profile_form.is_valid():
            # Save user info
            user_form.save()
            
            # Ensure the profile is saved with the current user
            profile = profile_form.save(commit=False)
            profile.user = user  # Explicitly set the user before saving
            profile.save()

            messages.success(request, "Profile updated successfully.")
            return redirect('profile')  # Redirect to profile page after saving
    else:
        # Pre-populate forms with the existing data
        user_form = UserUpdateForm(instance=user)
        profile_form = profile_form_class(instance=profile_instance)

    return render(request, 'core/auth/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })




# for admin only-----------------------------------------------
# Function to check if the user is an admin
def is_admin(user):
    return user.is_authenticated and user.role == CustomUser.Role.ADMIN

# 🔹 View: List all usersfrom django.views.generic import ListView
from .models import CustomUser  # Adjust import path as needed

class UserListView(ListView):
    model = CustomUser
    template_name = 'core/dashboards/admin/users/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return CustomUser.objects.select_related(
            'farmer', 'customer', 'deliverypersonnel', 'milloperator', 'admin'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_roles'] = {
            'ADMIN': 'Administrators',
            'FARMER': 'Farmers',
            'CUSTOMER': 'Customers',
            'DELIVERY': 'Delivery Personnel',
            'MILL_OPERATOR': 'Mill Operators',
        }
        return context

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




# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>paddy price
def set_paddy_price(request):
    if request.method == 'POST':
        form = PaddyPriceForm(request.POST)
        if form.is_valid():
            # Save the new paddy price
            form.save()
            return redirect('success_url')  # Redirect to a success page or dashboard
    else:
        form = PaddyPriceForm()

    return render(request, 'core/dashboards/admin/set_paddy_price.html', {'form': form})


def success_view(request):
    # Render a template or show a success message
    return render(request, 'core/dashboards/admin/success.html')




# View to add paddy supply
def record_supply_view(request):
    if request.method == 'POST':
        form = MillOperatorPaddySupplyForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Supply recorded successfully.")
            return redirect('supply_list')
    else:
        form = MillOperatorPaddySupplyForm()
    return render(request, 'core/all/record_supply.html', {'form': form})


@login_required
def approve_payment_view(request, supply_id):
    # Get the supply object by its ID
    supply = get_object_or_404(PaddySupply, id=supply_id)

    # Only allow the admin to approve the payment
    if request.user.role != request.user.Role.ADMIN:
        messages.error(request, "You do not have permission to approve payments.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminPaddyPaymentApprovalForm(request.POST)
        if form.is_valid():
            # Approve the payment and add the payment reference code
            form.approve(supply, request.user)
            messages.success(request, "Payment has been approved successfully.")
            return redirect('supply_list')
        else:
            messages.error(request, "There was an error approving the payment. Please check the details.")
    else:
        form = AdminPaddyPaymentApprovalForm()

    # Render the approval form page
    return render(request, 'core/all/approve_payment.html', {
        'form': form,
        'supply': supply
    })




login_required
def paddy_supply_list_view(request):
    user = request.user

    # Admin sees all supplies; mill operator sees only their recorded supplies
    if user.role == CustomUser.Role.ADMIN:
        supplies = PaddySupply.objects.select_related('farmer__user', 'mill_operator').all()
    elif user.role == CustomUser.Role.MILL_OPERATOR:
        supplies = PaddySupply.objects.select_related('farmer__user', 'mill_operator').filter(mill_operator=user)
    else:
        supplies = PaddySupply.objects.none()

    context = {
        'supplies': supplies
    }
    return render(request, 'core/all/paddy_supply_list.html', context)



#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 
@login_required
def inventory_view(request):
    # Get the inventories (assuming there's only one record of each)
    paddy_inventory = PaddyInventory.objects.first()
    processed_rice_inventory = ProcessedRiceInventory.objects.first()
    sold_rice_inventory = SoldRiceInventory.objects.first()

    return render(request, 'core/all/inventory.html', {
        'paddy_inventory': paddy_inventory,
        'processed_rice_inventory': processed_rice_inventory,
        'sold_rice_inventory': sold_rice_inventory
    })


@login_required
def process_rice_view(request):
    processed_quantity = None  # This will hold the decimal quantity for the view

    if request.method == 'POST':
        form = ProcessedRiceForm(request.POST, initial={'user_id': request.user.id})
        if form.is_valid():
            try:
                form.save()
                # Get updated processed rice quantity
                processed_inventory = ProcessedRiceInventory.objects.first()
                processed_quantity = processed_inventory.quantity if processed_inventory else Decimal('0.00')
                return render(request, 'core/all/process_rice_success.html', {
                    'quantity': processed_quantity
                })
            except ValueError as e:
                form.add_error(None, str(e))  # Show error at top of form
    else:
        form = ProcessedRiceForm(initial={'user_id': request.user.id})

    return render(request, 'core/all/process_rice.html', {'form': form})

@login_required
def processed_rice_success(request):
    return render(request, 'core/all/processed_rice_success.html')









# Optional: admin-only decorator
def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def package_list(request):
    packages = PackageSize.objects.all()
    return render(request, 'core/packages/package_list.html', {'packages': packages})

@user_passes_test(is_admin)
def package_create(request):
    if request.method == 'POST':
        form = PackageSizeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('package_list')
    else:
        form = PackageSizeForm()
    return render(request, 'core/packages/package_form.html', {'form': form})

@user_passes_test(is_admin)
def package_update(request, pk):
    package = get_object_or_404(PackageSize, pk=pk)
    if request.method == 'POST':
        form = PackageSizeForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            return redirect('package_list')
    else:
        form = PackageSizeForm(instance=package)
    return render(request, 'core/packages/package_form.html', {'form': form})

@user_passes_test(is_admin)
def package_delete(request, pk):
    package = get_object_or_404(PackageSize, pk=pk)
    if request.method == 'POST':
        package.delete()
        return redirect('package_list')
    return render(request, 'core/packages/package_confirm_delete.html', {'package': package})





from django.utils import timezone




@login_required
def place_order_view(request):
    packages = PackageSize.objects.all()

    if request.method == 'POST':
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.create(customer=customer)

        for package in packages:
            quantity = int(request.POST.get(f'package_{package.id}', 0))
            if quantity > 0:
                OrderItem.objects.create(
                    order=order,
                    package_size=package,
                    quantity=quantity
                )

        order.calculate_totals()
        return render(request, 'core/orders/order_success.html')

    return render(request, 'core/orders/place_order.html', {'packages': packages})


@login_required
def order_list(request):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'core/orders/order_list.html', {'orders': orders})


@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
    transaction = getattr(order, 'transaction', None)
    delivery = getattr(order, 'delivery', None)
    return render(request, 'core/orders/order_details.html', {
        'order': order,
        'transaction': transaction,
        'delivery': delivery,
    })


@login_required
def enter_transaction_code(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)

    if hasattr(order, 'transaction'):
        messages.warning(request, "You have already submitted a transaction code for this order.")
        return redirect('order_details', order_id=order.id)

    if request.method == 'POST':
        code = request.POST.get('transaction_code_customer')

        if code:
            Transaction.objects.create(order=order, transaction_code_customer=code)
            messages.success(request, "Transaction code submitted successfully!")
            return redirect('order_details', order_id=order.id)
        else:
            messages.error(request, "Please enter a valid transaction code.")

    return render(request, 'core/orders/enter_transaction_code.html', {'order': order})


@login_required
def track_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Restrict access if not their order
    if request.user.role == 'customer' and order.customer.user != request.user:
        return HttpResponseForbidden("You are not allowed to track this order.")

    delivery = Delivery.objects.filter(order=order).first()

    return render(request, 'core/orders/track_delivery.html', {
        'order': order,
        'delivery': delivery,
        'delivery_personnel': order.delivery_personnel,  # passed for display
    })









def is_admin(user):
    return user.is_authenticated and user.role == 'admin'





# @login_required(login_url='login')  # Ensure user is logged in
# @user_passes_test(is_admin, login_url='login')  # Ensure user is admin

def all_transactions(request):
    transactions = Transaction.objects.select_related('order', 'order__customer').order_by('-transaction_time')

    return render(request, 'core/orders/all_transactions.html', {
        'transactions': transactions
    })


def confirm_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if transaction.order.status == 'paid':
        messages.info(request, f"Transaction for Order #{transaction.order.id} is already confirmed.")
    else:
        if request.method == 'POST':
            # Save triggers order.status = 'paid' automatically
            transaction.save()
            messages.success(request, f"Transaction for Order #{transaction.order.id} confirmed successfully.")
            return redirect('order_list')

    return render(request, 'core/orders/confirm_transaction.html', {
        'transaction': transaction,
        'order': transaction.order,
    })




from django.db import transaction

def is_admin(user):
    return user.role == 'ADMIN'

def assign_delivery(request):
    if request.method == 'POST':
        form = AssignDeliveryForm(request.POST)

        if form.is_valid():
            order = form.cleaned_data['order']
            delivery_personnel = form.cleaned_data['delivery_personnel']

            order.delivery_personnel = delivery_personnel
            order.save()

            messages.success(request, "Delivery personnel assigned successfully!")
            return redirect('assign_delivery')
        else:
            messages.error(request, "Please fill out the form correctly.")
    else:
        form = AssignDeliveryForm()

    # Show eligible orders for assignment
    orders = Order.objects.filter(delivery_personnel__isnull=True, status='paid')\
                          .select_related('customer__user')\
                          .prefetch_related('items__package_size')\
                          .order_by('-created_at')

    return render(request, 'core/orders/assign_delivery.html', {
        'form': form,
        'orders': orders
    })





from django.http import JsonResponse
from django.template.loader import render_to_string
@login_required
def admin_order_list(request):
    all_orders = Order.objects.all().order_by('-created_at')
    return render(request, 'core/orders/admin_order_list.html', {'orders': all_orders})

@login_required
def admin_order_detail_ajax(request, pk):
    order = get_object_or_404(Order, pk=pk)
    html = render_to_string('core/orders/partials/order_detail_modal_content.html', {'order': order})
    return JsonResponse({'html': html})




@login_required
def update_delivery_status(request, order_id):
    # Ensure the logged-in user is a delivery personnel
    if request.user.role != CustomUser.Role.DELIVERY:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')

    # Get the logged-in delivery personnel
    try:
        delivery_personnel = DeliveryPersonnel.objects.get(user=request.user)
    except DeliveryPersonnel.DoesNotExist:
        messages.error(request, "Delivery personnel not found.")
        return redirect('login')

    # Get the order based on the passed order_id
    order = get_object_or_404(Order, id=order_id)

    # Check if the order is assigned to the logged-in delivery personnel
    if order.delivery_personnel != delivery_personnel:
        messages.error(request, "You are not assigned to this order.")
        return redirect('delivery_dashboard')

    # If the order is not yet delivered, allow the status update
    if order.status != 'delivered':
        if request.method == 'POST':
            # Update order status and other relevant fields
            order.mark_as_delivered()
            messages.success(request, "Order marked as delivered.")
            return redirect('delivery_dashboard')
    else:
        messages.error(request, "Order has already been delivered.")
        return redirect('delivery_dashboard')

    return render(request, 'core/orders/update_delivery_status.html', {'order': order})

