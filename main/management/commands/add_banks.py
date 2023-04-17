from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from ...models import Bank
import os
import requests

User = get_user_model()

class Command(BaseCommand):

    def handle(self, *args, **options):
        url="https://api.flutterwave.com/v3/banks/NG"
        res = requests.get(url, headers={'Authorization': os.getenv("FLW_SECRET_KEY")})
        data = res.json().get("data")
        
        banks = []
        for i in data:
            i.pop("id")
            banks.append(Bank(**i))
        Bank.objects.bulk_create(banks)
        