from django.core.management.base import BaseCommand, CommandError
from referal.models import ReferralBonus


class Command(BaseCommand):
    help = 'Create referrals'


    def handle(self, *args, **options):
        
        
        ReferralBonus.objects.create(
            percent  =  0.5,
            owner  = "referrer"
        )
        
        ReferralBonus.objects.create(
            percent  =  0,
            owner  = "referred"
        )
        
        
        self.stdout.write(self.style.SUCCESS("Successfully added referral bonuses"))