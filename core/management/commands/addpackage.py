from django.core.management.base import BaseCommand
from core.models import PackageSize

class Command(BaseCommand):
    help = 'Add default rice package sizes based on Kenya market'

    def handle(self, *args, **kwargs):
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
