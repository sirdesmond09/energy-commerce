from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from ...models import CalculatorItem

User = get_user_model()

class Command(BaseCommand):


    def handle(self, *args, **options):
        
        data = [
            {
            "name": "Refrigerator",
            "power": 150,
            "avg_hr_per_day": 24
        },
        {
            "name": "Air Conditioner",
            "power": 1000,
            "avg_hr_per_day": 4
        },
        {
            "name": "Television",
            "power": 80,
            "avg_hr_per_day": 5
        },
        {
            "name": "Electric Oven",
            "power": 2400,
            "avg_hr_per_day": 1
        },
        {
            "name": "Clothes Dryer",
            "power": 3000,
            "avg_hr_per_day": 1
        },
        {
            "name": "Electric Kettle",
            "power": 1500,
            "avg_hr_per_day": 0.5
        },
        {
            "name": "Dishwasher",
            "power": 1200,
            "avg_hr_per_day": 1
        },
        {
            "name": "Desktop Computer",
            "power": 200,
            "avg_hr_per_day": 5
        },
        {
            "name": "Laptop Computer",
            "power": 50,
            "avg_hr_per_day": 5
        },
        {
            "name": "WiFi Router",
            "power": 10,
            "avg_hr_per_day": 24
        },
        {
            "name": "LED Light Bulb",
            "power": 10,
            "avg_hr_per_day": 5
        },
        {
            "name": "Ceiling Fan",
            "power": 75,
            "avg_hr_per_day": 8
        },
        {
            "name": "Microwave",
            "power": 1000,
            "avg_hr_per_day": 0.5
        },
        {
            "name": "Toaster",
            "power": 800,
            "avg_hr_per_day": 0.25
        },
        {
            "name": "Coffee Maker",
            "power": 900,
            "avg_hr_per_day": 1
        },
        {
            "name": "Blender",
            "power": 500,
            "avg_hr_per_day": 0.25
        },
        {
            "name": "Food Processor",
            "power": 500,
            "avg_hr_per_day": 0.25
        },
        {
            "name": "Electric Griddle",
            "power": 1500,
            "avg_hr_per_day": 0.5
        },
        {
            "name": "Hair Dryer",
            "power": 1200,
            "avg_hr_per_day": 0.25
        },
        {
            "name": "Electric Heater",
            "power": 1500,
            "avg_hr_per_day": 4
        },
        {
            "name": "Smartphone Charger",
            "power": 5,
            "avg_hr_per_day": 2
        },
        {
            "name": "Tablet Charger",
            "power": 10,
            "avg_hr_per_day": 1
        },
        {
            "name": "Lamp",
            "power": 60,
            "avg_hr_per_day": 4
        },
        {
            "name": "Game Console",
            "power": 150,
            "avg_hr_per_day": 2
        },
        {
            "name": "DVD Player",
            "power": 20,
            "avg_hr_per_day": 2
        },
        {
            "name": "Electric Range",
            "power": 5000,
            "avg_hr_per_day": 1
        },
        {
            "name": "Dustbuster",
            "power": 15,
            "avg_hr_per_day": 0.25
        },
        {
            "name": "Vacuum Cleaner",
            "power": 1200,
            "avg_hr_per_day": 0.5
        },
        {
            "name": "Air Fryer",
            "power": 1400,
            "avg_hr_per_day": 0.25
        },
        {
            "name": "Electric Grill",
            "power": 1500,
            "avg_hr_per_day": 0.5
        },
        {
            "name": "Rice Cooker",
            "power": 500,
            "avg_hr_per_day": 1
        },
        {
            "name": "Humidifier",
            "power": 60,
            "avg_hr_per_day": 8
        },
        {
            "name": "Dehumidifier",
            "power": 500,
            "avg_hr_per_day": 4
        },
        {
            "name": "Smart Speaker",
            "power": 15,
            "avg_hr_per_day": 4
        },
        {
            "name": "Tablet",
            "power": 15,
            "avg_hr_per_day": 3
        },
        {
            "name": "Desktop Monitor",
            "power": 50,
            "avg_hr_per_day": 5
        },
        {
            "name": "Printer",
            "power": 500,
            "avg_hr_per_day": 1
        },
        {
            "name": "External Hard Drive",
            "power": 10,
            "avg_hr_per_day": 2
        }
        ]
        
        objs = []
        for item in data:
            objs.append(CalculatorItem(**item))
            
        CalculatorItem.objects.bulk_create(objs)
        
        self.stdout.write(self.style.SUCCESS("Successfully added items"))