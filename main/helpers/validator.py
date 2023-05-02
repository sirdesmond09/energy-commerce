import os
import requests
from rest_framework.exceptions import ValidationError
from django.utils import timezone

def payment_is_verified(trans_id):
    base_url = os.getenv("FLUTTER_VERIFICATION_URL")
    token = os.getenv("FLW_SECRET_KEY")
    url = base_url + f"{trans_id}/verify/"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        try:
            if res.json()["data"]["status"] == "successful":
                return True
            else:
                return False
            
        except Exception as e:
            raise ValidationError(str(e))
    else:
        return {"message": "payment not found"}
    

def calculate_start_date(days_ago):
    """Helper function to calculate start date"""
    return (timezone.now() - timezone.timedelta(days=days_ago)).date()