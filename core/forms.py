from time import timezone
from django import forms
from dal import autocomplete
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
)
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Delivery, Farmer, Customer, DeliveryPersonnel, MillOperator, Admin, Order, OrderItem, PackageSize, PaddyPrice, PaddySupply, ProcessedRice, SoldRiceInventory, Transaction
from django.contrib.auth import get_user_model


class BaseForm:
    """Base form class for common styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            widget = self.fields[field].widget
            if not isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({'class': 'form-control'})
            if self.fields[field].required:
                widget.attrs['required'] = 'required'

# ---------------- Authentication Forms ----------------

class UserLoginForm(BaseForm, AuthenticationForm):
    username = forms.CharField(label=_("Email or Username"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Email or Username'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})


class UserPasswordChangeForm(BaseForm, PasswordChangeForm):
    pass


class UserPasswordResetForm(BaseForm, PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'Enter your email'})
    )


class UserSetPasswordForm(BaseForm, SetPasswordForm):
    pass

# ---------------- Registration & Profile Forms ----------------

class UserRegistrationForm(BaseForm, forms.ModelForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_("Password must contain at least 8 characters including letters and numbers.")
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'role')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and not self.user.is_superuser:
            self.fields['role'].choices = [
                (CustomUser.Role.FARMER, _('Farmer')),
                (CustomUser.Role.CUSTOMER, _('Customer')),
            ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))
        if len(password1) < 8:
            raise forms.ValidationError(_("Password must be at least 8 characters long"))
        if password1.isdigit():
            raise forms.ValidationError(_("Password can't be entirely numeric"))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_profile(user)
        return user

    def save_profile(self, user):
        role = self.cleaned_data.get('role')
        if role == CustomUser.Role.FARMER:
            Farmer.objects.create(user=user)
        elif role == CustomUser.Role.CUSTOMER:
            Customer.objects.create(user=user)
        elif role == CustomUser.Role.DELIVERY:
            DeliveryPersonnel.objects.create(user=user)
        elif role == CustomUser.Role.MILL_OPERATOR:
            MillOperator.objects.create(user=user)
        elif role == CustomUser.Role.ADMIN:
            Admin.objects.create(user=user)

class UserUpdateForm(BaseForm, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')

# ---------------- Role-Based Profile Forms ----------------

class FarmerProfileForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ('bank_name', 'account_number')
        labels = {
            'bank_name': _('Bank Name'),
            'account_number': _('Account Number'),
        }

class CustomerProfileForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('delivery_address', 'preferred_payment_method')
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
        }

class DeliveryPersonnelProfileForm(BaseForm, forms.ModelForm):
    class Meta:
        model = DeliveryPersonnel
        fields = ('vehicle_type', 'vehicle_number', 'license_number', 'is_available')
        widgets = {
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MillOperatorProfileForm(BaseForm, forms.ModelForm):
    class Meta:
        model = MillOperator
        fields = ('shift', 'qualification')
        widgets = {
            'shift': forms.Select(attrs={'class': 'form-select'}),
        }

class AdminProfileForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Admin
        fields = ('admin_type', 'department')
        widgets = {
            'admin_type': forms.Select(attrs={'class': 'form-select'}),
        }



# paddy price

class PaddyPriceForm(forms.ModelForm):
    class Meta:
        model = PaddyPrice
        fields = ['price_per_kg']  # Only include price_per_kg as it is editable

#  paddy supply
class PaddySupplyForm(forms.ModelForm):
    class Meta:
        model = PaddySupply
        fields = ['farmer', 'quantity', 'quality_rating', 'moisture_content', 'status']

    farmer = forms.ModelChoiceField(
        queryset=Farmer.objects.all(),
        widget=autocomplete.ModelSelect2(url='farmer-autocomplete')  # Using the 'farmer-autocomplete' URL
    )






class MillOperatorPaddySupplyForm(forms.ModelForm):
    class Meta:
        model = PaddySupply
        fields = ['farmer', 'quantity', 'quality_rating', 'moisture_content']

        widgets = {
            'farmer': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quality_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'moisture_content': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            instance.save(user_id=user.id)
        else:
            instance.save()
        return instance



class AdminPaddyPaymentApprovalForm(forms.ModelForm):
    payment_reference_code = forms.CharField(
        max_length=100,
        required=True,
        help_text="Enter the payment reference code",
        widget=forms.TextInput(attrs={'placeholder': 'Payment Reference Code'})
    )

    class Meta:
        model = PaddySupply
        fields = ['payment_reference_code']  # Include only the payment_reference_code field

    def approve(self, instance, admin_user):
        """Approve the payment for the instance and set the payment reference code."""
        # Assign the payment reference code from the form
        instance.payment_reference_code = self.cleaned_data['payment_reference_code']
        # Call the approve_payment method to finalize the approval
        instance.approve_payment(admin_user)


class ProcessedRiceForm(forms.ModelForm):
    class Meta:
        model = ProcessedRice
        fields = ['quantity']  # Mill operator will enter the quantity of paddy processed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Auto-set the mill_operator field to the logged-in user
        self.fields['quantity'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter quantity of paddy processed (kg)'})

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Automatically assign the logged-in mill operator to the instance
        instance.mill_operator = get_user_model().objects.get(id=self.initial.get('user_id'))
        
        if commit:
            instance.save()
        return instance
    


class PackageSizeForm(forms.ModelForm):
    class Meta:
        model = PackageSize
        fields = ['weight_kg', 'label', 'price_per_package']
        widgets = {
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_package': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }




# from here customerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr 
from django.utils import timezone


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']  # Only 'status' is visible/editable in this form
        widgets = {
            'status': forms.Select(choices=Order.ORDER_STATUS_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Capture request for user info
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        order = super().save(commit=False)

        # Auto-assign the customer
        if self.request and hasattr(self.request.user, 'customer'):
            order.customer = self.request.user.customer

            # Auto-fill name and address from customer
            user = self.request.user
            customer_profile = user.customer

            if not order.delivery_address:
                order.delivery_address = customer_profile.delivery_address

            if not order.customer_name:
                order.customer_name = f"{user.first_name} {user.last_name}"

        if commit:
            order.save()
        return order





class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['package_size', 'quantity']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive integer.")
        return quantity


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_code_customer']
        widgets = {
            'transaction_code_customer': forms.TextInput(attrs={'placeholder': 'Enter MPESA code'}),
        }


# hiii ziii
class SoldRiceInventoryForm(forms.ModelForm):
    class Meta:
        model = SoldRiceInventory
        fields = ['quantity']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError("Sold rice quantity cannot be negative.")
        return quantity



class AssignDeliveryForm(forms.Form):
    order = forms.ModelChoiceField(
        queryset=Order.objects.filter(
            delivery_personnel__isnull=True,
            status='paid'
        ).order_by('-created_at'),
        label='Select Order',
        empty_label="-- Select Order --",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    delivery_personnel = forms.ModelChoiceField(
        queryset=DeliveryPersonnel.objects.exclude(
            id__in=Order.objects.filter(
                status='paid',
                delivery_personnel__isnull=False
            ).values_list('delivery_personnel__id', flat=True)
        ),
        label='Select Delivery Personnel',
        empty_label="-- Select Delivery Personnel --",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )



class DeliveryUpdateForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['is_delivered']
        widgets = {
            'is_delivered': forms.CheckboxInput(),
        }

    def save(self, commit=True):
        delivery = super().save(commit=False)

        # Auto-set delivery date when marked as delivered
        if delivery.is_delivered and not delivery.delivery_date:
            delivery.delivery_date = timezone.now()

        if commit:
            delivery.save()
        return delivery