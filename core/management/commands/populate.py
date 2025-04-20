import random
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import (
    PackageSize, Farmer, Customer, DeliveryPersonnel,
    MillOperator, Admin, PaddyPrice
)
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Populate the system with initial data: users, package sizes, and paddy price.'

    def handle(self, *args, **options):
        self.create_package_sizes()
        self.create_users()
        self.create_paddy_price()

    def create_package_sizes(self):
        self.stdout.write(self.style.MIGRATE_HEADING('\nAdding default rice package sizes...'))
        packages = [
            {"weight_kg": 100.00, "label": "100kg Bag", "price_per_package": 7500.00},
            {"weight_kg": 50.00, "label": "50kg Bag", "price_per_package": 3800.00},
            {"weight_kg": 25.00, "label": "25kg Bag", "price_per_package": 2000.00},
            {"weight_kg": 10.00, "label": "10kg Bag", "price_per_package": 850.00},
            {"weight_kg": 5.00, "label": "5kg Bag", "price_per_package": 450.00},
            {"weight_kg": 2.00, "label": "2kg Bag", "price_per_package": 190.00},
        ]

        for pkg in packages:
            obj, created = PackageSize.objects.get_or_create(
                weight_kg=pkg["weight_kg"],
                defaults={
                    "label": pkg["label"],
                    "price_per_package": pkg["price_per_package"],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added: {obj}"))
            else:
                self.stdout.write(self.style.WARNING(f"Skipped (already exists): {obj}"))

    def create_users(self):
        self.stdout.write(self.style.MIGRATE_HEADING('\nCreating users for each role...'))
        User = get_user_model()
        roles = User.Role.choices
        users_per_role = 4

        kenyan_first_names = [
            'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 
            'Thomas', 'Daniel', 'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 
            'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen', 'Kamau', 'Wanjiru', 'Njoroge',
            'Nyambura', 'Kipchoge', 'Auma', 'Omondi', 'Atieno', 'Maina', 'Wambui'
        ]
        kenyan_last_names = [
            'Mwangi', 'Ochieng', 'Kamau', 'Kipchoge', 'Omondi', 'Maina', 'Ndungu', 
            'Wambua', 'Kariuki', 'Njoroge', 'Auma', 'Akinyi', 'Atieno', 'Nyambura', 
            'Wanjiru', 'Njeri', 'Wambui', 'Muthoni', 'Nyokabi', 'Wairimu'
        ]
        kenyan_banks = [
            'Equity Bank', 'KCB Bank', 'Cooperative Bank', 'Standard Chartered', 
            'Barclays Bank', 'Absa Bank', 'NCBA Bank', 'DTB Bank'
        ]
        kenyan_locations = [
            {"location": "Kikuyu Town", "constituency": "Kikuyu", "county": "Kiambu", "pobox": "P.O. Box 10200 - Kikuyu"},
            {"location": "Lang'ata", "constituency": "Lang'ata", "county": "Nairobi", "pobox": "P.O. Box 00509 - Lang'ata"},
            {"location": "Likoni", "constituency": "Likoni", "county": "Mombasa", "pobox": "P.O. Box 80100 - Mombasa"},
            {"location": "Rongai", "constituency": "Kajiado North", "county": "Kajiado", "pobox": "P.O. Box 01100 - Rongai"},
            {"location": "Kericho Town", "constituency": "Ainamoi", "county": "Kericho", "pobox": "P.O. Box 20200 - Kericho"},
            {"location": "Kisumu Central", "constituency": "Kisumu Central", "county": "Kisumu", "pobox": "P.O. Box 40100 - Kisumu"},
            {"location": "Eldoret", "constituency": "Ainabkoi", "county": "Uasin Gishu", "pobox": "P.O. Box 30100 - Eldoret"},
            {"location": "Nyeri Town", "constituency": "Nyeri Town", "county": "Nyeri", "pobox": "P.O. Box 10100 - Nyeri"},
        ]

        for role in roles:
            role_code = role[0]
            role_name = role[1]
            self.stdout.write(self.style.SUCCESS(f'\nCreating {users_per_role} {role_name}s...'))

            for i in range(users_per_role):
                first_name = random.choice(kenyan_first_names)
                last_name = random.choice(kenyan_last_names)
                email = f"{first_name.lower()}.{last_name.lower()}{i}@{role_name.lower().replace(' ', '')}.com"
                username = f"{first_name.lower()}_{last_name.lower()}_{role_code.lower()}_{i}"
                phone_number = f"2547{random.randint(10, 99)}{random.randint(100000, 999999)}"

                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password='pass123',
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    role=role_code
                )

                if role_code == User.Role.FARMER:
                    Farmer.objects.create(
                        user=user,
                        bank_name=random.choice(kenyan_banks),
                        account_number=f"{random.randint(1000000000, 9999999999)}",
                    )
                elif role_code == User.Role.CUSTOMER:
                    loc = random.choice(kenyan_locations)
                    delivery_address = f"{loc['location']}, {loc['constituency']} Constituency, {loc['county']} County, {loc['pobox']}"
                    Customer.objects.create(
                        user=user,
                        delivery_address=delivery_address,
                        preferred_payment_method=random.choice(['MPESA', 'CARD'])
                    )
                elif role_code == User.Role.DELIVERY:
                    DeliveryPersonnel.objects.create(
                        user=user,
                        vehicle_type=random.choice(['Pickup Truck', 'Lorry', 'Motorcycle', 'Van']),
                        vehicle_number=f"K{random.choice(['A','B','C'])} {random.randint(100, 999)}{random.choice(['A','B','C'])}",
                        is_available=random.choice([True, False]),
                        license_number=f"DL{random.randint(1000000, 9999999)}"
                    )
                elif role_code == User.Role.MILL_OPERATOR:
                    MillOperator.objects.create(
                        user=user,
                        shift=random.choice(['MORNING', 'EVENING', 'NIGHT']),
                        qualification=random.choice([
                            'Certificate in Milling',
                            'Diploma in Food Processing',
                            'Vocational Training'
                        ])
                    )
                elif role_code == User.Role.ADMIN:
                    Admin.objects.create(
                        user=user,
                        admin_type=random.choice(['STANDARD']),
                        department=random.choice([
                            'Operations',
                            'Management',
                            'Finance',
                            'Human Resources'
                        ])
                    )

                self.stdout.write(f"Created {role_name}: {first_name} {last_name} ({email})")

    def create_paddy_price(self):
        self.stdout.write(self.style.MIGRATE_HEADING('\nAdding default paddy price...'))
        if not PaddyPrice.objects.exists():
            price = PaddyPrice.objects.create(price_per_kg=45.00)
            self.stdout.write(self.style.SUCCESS(f"Added paddy price: {price}"))
        else:
            latest_price = PaddyPrice.objects.latest('effective_date')
            self.stdout.write(self.style.WARNING(f"Paddy price already exists (latest: {latest_price})"))
