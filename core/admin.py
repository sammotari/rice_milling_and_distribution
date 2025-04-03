from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Farmer, Customer, DeliveryPersonnel, MillOperator, Admin,
    PaddyType, PaddySupply, RiceProduct, Order, OrderItem,
    Delivery, CustomerPayment, FarmerPayment, Notification
)

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_photo')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# Farmer Admin
@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank_name', 'account_number', 'total_paddy_supplied')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'account_number')
    raw_id_fields = ('user',)

# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'delivery_address')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)

# Delivery Personnel Admin
@admin.register(DeliveryPersonnel)
class DeliveryPersonnelAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_type', 'vehicle_number', 'is_available')
    list_filter = ('is_available', 'vehicle_type')
    search_fields = ('user__email', 'vehicle_number')
    raw_id_fields = ('user',)

# Mill Operator Admin
@admin.register(MillOperator)
class MillOperatorAdmin(admin.ModelAdmin):
    list_display = ('user', 'shift', 'qualification')
    list_filter = ('shift',)
    search_fields = ('user__email', 'qualification')
    raw_id_fields = ('user',)

# Admin Admin
@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin_type', 'department')
    list_filter = ('admin_type',)
    search_fields = ('user__email', 'department')
    raw_id_fields = ('user',)

# Paddy Type Admin
@admin.register(PaddyType)
class PaddyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_kg')
    search_fields = ('name',)

# Paddy Supply Admin
@admin.register(PaddySupply)
class PaddySupplyAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'paddy_type', 'quantity', 'supply_date', 'status')
    list_filter = ('status', 'quality_rating', 'paddy_type')
    search_fields = ('farmer__user__email', 'paddy_type__name')
    raw_id_fields = ('farmer', 'mill_operator')
    date_hierarchy = 'supply_date'

# Rice Product Admin
@admin.register(RiceProduct)
class RiceProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'paddy_type', 'stock_quantity', 'price_per_kg', 'is_organic')
    list_filter = ('is_organic', 'paddy_type')
    search_fields = ('name', 'paddy_type__name')
    readonly_fields = ('display_image',)
    
    def display_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="150" height="150" />'
        return "No Image"
    display_image.allow_tags = True
    display_image.short_description = 'Image Preview'

# Order Item Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('product',)

# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'total_amount', 'status')
    list_filter = ('status',)
    search_fields = ('customer__user__email', 'id')
    date_hierarchy = 'order_date'
    inlines = [OrderItemInline]
    raw_id_fields = ('customer',)

# Delivery Admin
@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_person', 'status', 'assigned_date')
    list_filter = ('status',)
    search_fields = ('order__id', 'delivery_person__user__email')
    raw_id_fields = ('order', 'delivery_person')
    date_hierarchy = 'assigned_date'

# Customer Payment Admin
@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'payment_method', 'status', 'payment_date')
    list_filter = ('status', 'payment_method')
    search_fields = ('order__id', 'transaction_reference')
    date_hierarchy = 'payment_date'
    raw_id_fields = ('order',)

# Farmer Payment Admin
@admin.register(FarmerPayment)
class FarmerPaymentAdmin(admin.ModelAdmin):
    list_display = ('paddy_supply', 'amount', 'payment_method', 'status', 'processed_by')
    list_filter = ('status', 'payment_method')
    search_fields = ('paddy_supply__id', 'transaction_reference')
    raw_id_fields = ('paddy_supply', 'processed_by')
    date_hierarchy = 'payment_date'

# Notification Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_read', 'timestamp', 'notification_type')
    list_filter = ('is_read', 'notification_type')
    search_fields = ('user__email', 'message')
    date_hierarchy = 'timestamp'
    raw_id_fields = ('user',)