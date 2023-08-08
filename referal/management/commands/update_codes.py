from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from accounts.helpers.generators import generate_referral_code

User = get_user_model()

class Command(BaseCommand):
    help = 'Create referrals'


    def handle(self, *args, **options):
        
        
        users = User.objects.filter(role="user")
        
        for user in users:
            user.referral_code = generate_referral_code()
            user.save()
        
        
        self.stdout.write(self.style.SUCCESS("Successfully added updated referral codes"))