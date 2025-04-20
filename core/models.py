import uuid
from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.contrib.auth import get_user_model


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        if not username:
            raise ValueError(_('The Username must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', CustomUser.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Role(models.TextChoices):
        FARMER = 'FARMER', 'Farmer'
        CUSTOMER = 'CUSTOMER', 'Customer'
        DELIVERY = 'DELIVERY', 'Delivery Personnel'
        MILL_OPERATOR = 'MILL_OPERATOR', 'Mill Operator'
        ADMIN = 'ADMIN', 'Admin'

    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)

    role = models.CharField(max_length=20, choices=Role.choices)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_profile(self):
        if hasattr(self, 'farmer'):
            return self.farmer
        elif hasattr(self, 'customer'):
            return self.customer
        elif hasattr(self, 'deliverypersonnel'):
            return self.deliverypersonnel
        elif hasattr(self, 'milloperator'):
            return self.milloperator
        elif hasattr(self, 'admin'):
            return self.admin
        return None

    objects = CustomUserManager()

    def __str__(self):
        return self.email


    
class Farmer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    # total_paddy_supplied = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    preferred_payment_method = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class DeliveryPersonnel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=20)
    is_available = models.BooleanField(default=True)
    license_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class MillOperator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Shift(models.TextChoices):
        MORNING = 'MORNING', 'Morning Shift'
        EVENING = 'EVENING', 'Evening Shift'
        NIGHT = 'NIGHT', 'Night Shift'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    shift = models.CharField(max_length=10, choices=Shift.choices)
    qualification = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class AdminType(models.TextChoices):
        STANDARD = 'STANDARD', 'Standard Admin'
        SUPER = 'SUPER', 'Super Admin'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    admin_type = models.CharField(max_length=10, choices=AdminType.choices)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>paddy price
class PaddyPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paddy Price: {self.price_per_kg} per kg (Effective from {self.effective_date})"





User = get_user_model()
from django.db.models.signals import post_save

# Define the PaddySupply model (as per your earlier code)
class PaddySupply(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('rejected', 'Rejected'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey('Farmer', on_delete=models.CASCADE, related_name='paddy_supplies')
    mill_operator = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_supplies')

    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="In kilograms")
    quality_rating = models.PositiveIntegerField(help_text="Rating from 1 (lowest) to 5 (highest)")
    moisture_content = models.DecimalField(max_digits=5, decimal_places=2, help_text="Moisture percentage")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Received')

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0.00)

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid'
    )
    payment_approved_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_paddy_payments')
    payment_approved_at = models.DateTimeField(null=True, blank=True)

    # New field for payment reference code
    payment_reference_code = models.CharField(max_length=100, null=True, blank=True, help_text="Reference code for payment")

    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Supply by {self.farmer.user.get_full_name()} - {self.quantity}kg"

    def save(self, *args, **kwargs):
        if not self.mill_operator:
            user_id = kwargs.pop('user_id', None)
            if user_id:
                user = get_user_model().objects.get(id=user_id)
                if user.role != get_user_model().Role.MILL_OPERATOR:
                    raise ValueError("Only mill operators can record paddy supply.")
                self.mill_operator = user

        from core.models import PaddyPrice  # Avoid circular imports
        latest_price = PaddyPrice.objects.order_by('-effective_date').first()
        if not latest_price:
            raise ValueError("No paddy price available. Please reach out to the administrator")

        # Ensure both `self.quantity` and `latest_price.price_per_kg` are Decimal
        self.total_amount = Decimal(str(self.quantity)) * Decimal(str(latest_price.price_per_kg))

        if self.pk is None:
            self.farmer.total_paddy_supplied += self.quantity
            self.farmer.save()

        super().save(*args, **kwargs)



    def approve_payment(self, admin_user):
        """Approve the payment for the paddy supply."""
        if admin_user.role != get_user_model().Role.ADMIN:
            raise PermissionError("Only admins can approve payments.")
        
        self.payment_status = 'paid'  # Change status to 'paid'
        self.payment_approved_by = admin_user  # Set the admin user who approved
        self.payment_approved_at = timezone.now()  # Set the approval timestamp
        self.save()  # Save the updated record

    def display_bank_details(self):
        return f"{self.farmer.bank_name} - {self.farmer.account_number}"


class ProcessedRiceInventory(models.Model):
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text="Total processed rice in kilograms"
    )

    def __str__(self):
        return f"Processed Rice Inventory: {self.quantity}kg"

    def update_inventory(self, quantity):
        """Increase inventory when paddy is processed into rice."""
        self.quantity += Decimal(str(quantity))
        self.save()


class PaddyInventory(models.Model):
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text="Total unprocessed paddy in kilograms"
    )

    def __str__(self):
        return f"Paddy Inventory: {self.quantity}kg"

    def update_inventory(self, quantity):
        """Increase inventory when new paddy is supplied."""
        self.quantity += Decimal(str(quantity))
        self.save()

    def reduce_inventory(self, quantity):
        """Reduce inventory when paddy is processed into rice."""
        quantity_decimal = Decimal(str(quantity))
        if self.quantity >= quantity_decimal:
            self.quantity -= quantity_decimal
            self.save()
        else:
            raise ValueError("Insufficient paddy inventory to reduce.")


class ProcessedRice(models.Model):
    mill_operator = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='processed_rice'
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="In kilograms"
    )

    def __str__(self):
        return f"Processed by {self.mill_operator} - {self.quantity} kg"


# Signal to update paddy inventory when new supply is added
@receiver(post_save, sender='core.PaddySupply')
def update_paddy_inventory_on_supply(sender, instance, created, **kwargs):
    if created:
        paddy_inventory, _ = PaddyInventory.objects.get_or_create(id=1)
        paddy_inventory.update_inventory(Decimal(str(instance.quantity)))


# Signal to reduce paddy inventory and increase processed rice inventory
@receiver(post_save, sender=ProcessedRice)
@transaction.atomic
def update_inventory_on_processed_rice(sender, instance, created, **kwargs):
    if created:
        paddy_quantity = Decimal(str(instance.quantity))

        with transaction.atomic():
            paddy_inventory = PaddyInventory.objects.select_for_update().first()
            if not paddy_inventory:
                raise ValueError("Paddy inventory not found")

            if paddy_inventory.quantity < paddy_quantity:
                raise ValueError("Insufficient paddy inventory")

            paddy_inventory.reduce_inventory(paddy_quantity)

            processed_rice_inventory, _ = ProcessedRiceInventory.objects.select_for_update().get_or_create(id=1)
            processed_rice_inventory.quantity += paddy_quantity
            processed_rice_inventory.save()






# customer package

class PackageSize(models.Model):
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 50.00, 25.00
    label = models.CharField(max_length=50)  # e.g., "50kg Bag"
    price_per_package = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 1500.00

    def __str__(self):
        return f"{self.label} - KES {self.price_per_package}"



class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255, blank=True)  # New field
    delivery_address = models.TextField(blank=True, null=True)    # Fetched from Customer
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Add phone number field

    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    delivery_personnel = models.ForeignKey(DeliveryPersonnel, null=True, blank=True, on_delete=models.SET_NULL)
    delivery_date = models.DateTimeField(null=True, blank=True)

    total_kg = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0.00)

    def __str__(self):
        return f"Order #{self.id} for {self.customer.user.username}"

    def calculate_totals(self):
        total_kg = 0
        total_amount = 0
        for item in self.items.all():
            total_kg += item.get_total_kg()
            total_amount += item.get_total_amount()

        self.total_kg = total_kg
        self.total_amount = total_amount
        self.save()


    def save(self, *args, **kwargs):
        # Auto-set delivery address and customer name from Customer profile if not already set
        if self.customer:
            if not self.delivery_address and self.customer.delivery_address:
                self.delivery_address = self.customer.delivery_address

            if not self.customer_name:
                user = self.customer.user
                self.customer_name = f"{user.first_name} {user.last_name}"

            if not self.phone_number and self.customer:
                self.phone_number = self.customer.user.phone_number  # Assuming 'phone_number' exists in the Customer model

        super().save(*args, **kwargs)


    
    # models.py (Order)
    def assign_delivery(self, delivery_personnel):
        """Assign the delivery personnel to the order."""
        if self.status == 'paid':  # Only assign delivery when the order is paid
            self.delivery_personnel = delivery_personnel
            self.save()
            return True
        else:
            raise ValueError("The order must be paid before assigning delivery personnel.")

    def mark_as_delivered(self):
        """Mark the order as delivered."""
        if self.status == 'paid':
            self.status = 'delivered'
            self.save()
        else:
            raise ValueError("Only paid orders can be marked as delivered.")
    





class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    package_size = models.ForeignKey(PackageSize, on_delete=models.CASCADE)  # Link to PackageSize model
    quantity = models.IntegerField(help_text="Quantity of the ordered package")

    def __str__(self):
        return f"Order Item {self.id} for Order #{self.order.id}"

    def get_total_kg(self):
        """Calculate total kilograms for this item based on quantity and package size."""
        return self.package_size.weight_kg * self.quantity

    def get_total_amount(self):
        """Calculate total amount for this item based on quantity and price per package."""
        return self.package_size.price_per_package * self.quantity







class Transaction(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    transaction_code_customer = models.CharField(max_length=100, help_text="MPESA or similar transaction code entered by customer")
    transaction_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction for Order #{self.order.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Automatically confirm transaction and update order status
        self.order.status = 'paid'
        self.order.save()






class SoldRiceInventory(models.Model):
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total rice sold in kilograms"
    )

    def __str__(self):
        return f"Sold Rice Inventory: {self.quantity}kg"

    def update_inventory(self, quantity):
        """Increase inventory when rice is sold."""
        # Ensure both sides are Decimal
        quantity = Decimal(str(quantity))
        current_quantity = Decimal(str(self.quantity))
        self.quantity = current_quantity + quantity
        self.save()


# Signal to update SoldRiceInventory and ProcessedRiceInventory when Order is confirmed






@receiver(post_save, sender=Transaction)
@transaction.atomic
def update_inventory_on_transaction(sender, instance, created, **kwargs):
    if created:
        order = instance.order

        # Ensure the order has updated totals
        if order.total_kg == 0:
            order.calculate_totals()

        total_kg_sold = Decimal(str(order.total_kg))  # <--- FIXED TYPE

        with transaction.atomic():
            processed_inventory = ProcessedRiceInventory.objects.select_for_update().first()
            if not processed_inventory:
                raise ValueError("Processed rice inventory not found")

            if processed_inventory.quantity < total_kg_sold:
                raise ValueError("Insufficient processed rice inventory")

            processed_inventory.quantity -= total_kg_sold
            processed_inventory.save()

            sold_inventory, _ = SoldRiceInventory.objects.select_for_update().get_or_create(id=1)
            sold_inventory.quantity += total_kg_sold
            sold_inventory.save()



class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_personnel = models.ForeignKey(DeliveryPersonnel, on_delete=models.SET_NULL, null=True)
    delivery_address = models.TextField()
    delivery_date = models.DateTimeField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"Delivery for Order #{self.order.id}"

    def mark_as_delivered(self):
        self.is_delivered = True
        self.delivery_date = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        # Automatically fetch address from customer if not set
        if not self.delivery_address and self.order.customer:
            self.delivery_address = self.order.customer.address
        super().save(*args, **kwargs)