from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from ...models import ModuleAccess

User = get_user_model()

class Command(BaseCommand):


    def handle(self, *args, **options):
        
        modules = [
  {
    "name": 'Vendors',
    "url": '/dashboard/vendors'
  },
  {
    "url": '/dashboard/orders',
    "name": 'Orders'
  },
  {
    "name": 'Customers',
    "url": '/dashboard/customers'
  },
  {
    "name": 'Categories',
    "url": '/dashboard/categories'
  },
  {
    "name": 'Products',
    "url": '/dashboard/products'
  },
  {
    "name": 'Payments and Loans',
    "url": '/dashboard/payments'
  },
  {
    "name": 'Staff',
    "url": '/dashboard/staff'
  },
  {
    "name": 'Roles/Permissions',
    "url": '/dashboard/roles'
  },
  {
    "url": '/dashboard/payouts',
    "name": 'Payouts'
  },
  {
    "name": 'FAQs',
    "url": '/dashboard/faqs'
  },
  {
    "name": 'Calculator Items',
    "url": '/dashboard/calculator-items'
  }
]
        
        objs = []
        for item in modules:
            objs.append(ModuleAccess(**item))
            
        ModuleAccess.objects.bulk_create(objs)
        
        self.stdout.write(self.style.SUCCESS("Successfully added modules"))
        
       