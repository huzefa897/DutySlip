from django.core.management.base import BaseCommand
from api.models import Car


class Command(BaseCommand):
    help = 'Seed car catalogue'

    def handle(self, *args, **kwargs):
        cars = [
            {"name": "Ute",         "base_rate": 100, "extra_km_rate": 1.20, "extra_hr_rate": 12},
            {"name": "Camry",       "base_rate": 500, "extra_km_rate": 2.50, "extra_hr_rate": 25},
            {"name": "HiAce",       "base_rate": 350, "extra_km_rate": 2.00, "extra_hr_rate": 20},
            {"name": "LandCruiser", "base_rate": 700, "extra_km_rate": 3.50, "extra_hr_rate": 35},
            {"name": "Corolla",     "base_rate": 280, "extra_km_rate": 1.80, "extra_hr_rate": 18},
        ]

        for car_data in cars:
            car, created = Car.objects.get_or_create(
                name=car_data["name"],
                defaults=car_data
            )
            if created:
                self.stdout.write(f"  Created: {car.name}")
            else:
                self.stdout.write(f"  Already exists: {car.name}")

        self.stdout.write(self.style.SUCCESS("Car seeding complete."))