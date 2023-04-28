from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from ...models import ProductCategory, Documentation 

User = get_user_model()

class Command(BaseCommand):


    def handle(self, *args, **options):
        
        cat_data = [
            {
            "name": "Battery",
            "desc": "This is a Battery",
            "img": None
        },
            {
            "name": "Inverter",
            "desc": "This is an Inverter",
            "img": None
        },
            {
            "name": "Complete Solution",
            "desc": "This is a Complete Solution",
            "img": None
        },
            {
            "name": "Home appliance",
            "desc": "This is a Home appliance",
            "img": None
        },
            {
            "name": "Accessory",
            "desc": "This is an Accessory",
            "img": None
        },
            {
            "name": "Solar Panel",
            "desc": "This is a solar panel",
            "img": None
        },
        
        ]
        
        objs = []
        for item in cat_data:
            objs.append(ProductCategory(**item))
            
        ProductCategory.objects.bulk_create(objs)
        
        self.stdout.write(self.style.SUCCESS("Successfully added categories"))
        
        
        doc_data = [
            {
            "name": "terms and condition",
            "data": "..."
        },
            {
            "name": "privacy policy",
            "data": "..."
        },
            {
            "name": "how to buy and sell",
            "data":"..."

        }
        
        ]
        
        objs = []
        for item in doc_data:
            objs.append(Documentation(**item))
            
        Documentation.objects.bulk_create(objs)
        
        self.stdout.write(self.style.SUCCESS("Successfully added page documentations"))
        
        
        
        