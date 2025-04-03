from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
)
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Farmer, Customer, DeliveryPersonnel, MillOperator, Admin

class BaseForm:
    """Base form class for common styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxInput):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            if self.fields[field].required:
                self.fields[field].widget.attrs['required'] = 'required'

# Authentication Forms
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

# User Management Forms
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
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'profile_photo')
        widgets = {
            'profile_photo': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

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
