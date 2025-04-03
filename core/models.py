import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
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
        """
        Create and save a SuperUser with the given email and password.
        """
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
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        default=None
    )

    def get_profile_photo_url(self):
        if self.profile_photo and hasattr(self.profile_photo, 'url'):
            return self.profile_photo.url
        return '/static/core/img/default-profile.png'
    
    role = models.CharField(max_length=20, choices=Role.choices)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_profile(self):
        """
        Get the profile object based on user role
        """
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
    total_paddy_supplied = models.DecimalField(max_digits=10, decimal_places=2, default=0)

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

class PaddyType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    ideal_climate = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class PaddySupply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class QualityRating(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        PREMIUM = 'PREMIUM', 'Premium'

    class SupplyStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        REJECTED = 'REJECTED', 'Rejected'

    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    paddy_type = models.ForeignKey(PaddyType, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    supply_date = models.DateTimeField(auto_now_add=True)
    mill_operator = models.ForeignKey(MillOperator, on_delete=models.SET_NULL, null=True, blank=True)
    quality_rating = models.CharField(max_length=10, choices=QualityRating.choices)
    status = models.CharField(max_length=10, choices=SupplyStatus.choices, default=SupplyStatus.PENDING)
    moisture_content = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.farmer} - {self.paddy_type} ({self.quantity}kg)"

class RiceProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    paddy_type = models.ForeignKey(PaddyType, on_delete=models.CASCADE)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='rice_products/', null=True, blank=True)
    packaging_size = models.CharField(max_length=50, blank=True)
    is_organic = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    special_instructions = models.TextField(blank=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(RiceProduct, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total_price(self):
        return self.quantity * self.price_per_kg

    def __str__(self):
        return f"{self.quantity}kg of {self.product} in Order #{self.order.id}"

class Delivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class DeliveryStatus(models.TextChoices):
        ASSIGNED = 'ASSIGNED', 'Assigned'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        FAILED = 'FAILED', 'Failed'

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(DeliveryPersonnel, on_delete=models.SET_NULL, null=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=DeliveryStatus.choices, default=DeliveryStatus.ASSIGNED)
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id}"

class CustomerPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CARD = 'CARD', 'Credit/Debit Card'
        MOBILE = 'MOBILE', 'Mobile Money'
        BANK = 'BANK', 'Bank Transfer'

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_reference = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Customer Payment for Order #{self.order.id} - {self.status}"

class FarmerPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    class PaymentMethod(models.TextChoices):
        BANK = 'BANK', 'Bank Transfer'
        MOBILE = 'MOBILE', 'Mobile Money'
        CASH = 'CASH', 'Cash'

    paddy_supply = models.ForeignKey(PaddySupply, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_reference = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   limit_choices_to={'role__in': [CustomUser.Role.ADMIN, CustomUser.Role.MILL_OPERATOR]})
    notes = models.TextField(blank=True)
    payment_period_start = models.DateField()
    payment_period_end = models.DateField()

    def __str__(self):
        return f"Farmer Payment for Supply #{self.paddy_supply.id} - {self.status}"

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=200, blank=True)
    notification_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Notification for {self.user} - {'Read' if self.is_read else 'Unread'}"