import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Farmer, Customer, DeliveryPersonnel, MillOperator, Admin
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Generates 4 users for each role in the system'

    def handle(self, *args, **options):
        User = get_user_model()
        roles = User.Role.choices
        users_per_role = 4
        
        # Kenyan names datasets
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
        
        kenyan_banks = ['Equity Bank', 'KCB Bank', 'Cooperative Bank', 'Standard Chartered', 
                       'Barclays Bank', 'Absa Bank', 'NCBA Bank', 'DTB Bank']
        
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
                
                # Create user
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password='pass123',
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    role=role_code
                )
                
                # Create role-specific profile
                if role_code == User.Role.FARMER:
                    Farmer.objects.create(
                        user=user,
                        bank_name=random.choice(kenyan_banks),
                        account_number=f"{random.randint(1000000000, 9999999999)}",
                    )
                elif role_code == User.Role.CUSTOMER:
                    Customer.objects.create(
                        user=user,
                        delivery_address=fake.address(),
                        preferred_payment_method=random.choice(['MPESA', 'CASH', 'CARD'])
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
                        admin_type=random.choice(['STANDARD', 'SUPER']),
                        department=random.choice([
                            'Operations',
                            'Management',
                            'Finance',
                            'Human Resources'
                        ])
                    )
                
                self.stdout.write(f"Created {role_name}: {first_name} {last_name} ({email})")
        
        self.stdout.write(self.style.SUCCESS('\nSuccessfully created all users!'))