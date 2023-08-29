from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from ...models import CaseType, CaseMinorCategory, CaseSubCategory

User = get_user_model()

class Command(BaseCommand):


    def handle(self, *args, **options):
        
        case_types = ['Complaint', "Request", "Enquiry"]
        
        for case in case_types:
            CaseType.objects.create(name=case)
            
            
        
        
        
        
        self.stdout.write(self.style.SUCCESS("Successfully added items"))