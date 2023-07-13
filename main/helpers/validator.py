import json
import os
import requests
from rest_framework.exceptions import ValidationError
from django.utils import timezone

from main.helpers.encryption import decrypt_data, encrypt_data

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




def validate_pws(ref):
    
    
    """Validate the Pay with specta payment on core-banking API"""
    payload = {
        "reference" : ref
    }
        
        
    pre_encoded_data = {
        "queryParameters": [],
        "headers": {
            "x-ApiKey": os.getenv("SPECTA_API_KEY")
        },
        "jsonBody": json.dumps(payload)
    }
    
    encoded_str = encrypt_data(pre_encoded_data)
    
    data = { "encryptedPayLoad": encoded_str,
        "applicationEndpoint": "/api/services/app/Purchase/RequeryFailedPurchase", 
        "httpMethod": 2
        } 
    
    res = requests.post(url=os.getenv("SPECTA_URL"),
                      json=data,
                      headers={"Authorization": f"Bearer {os.getenv('SPECTA_API_TOKEN')}",
                               "content-type":'application/json'})
        
    response = res.json().get('content')
    data = json.loads(decrypt_data(response))
    
    if data.get("status") == 404:
        return False
    return True
    
    # {'result': {'status': 404, 'data': None, 'message': 'Not Found'}, 'targetUrl': None, 'success': True, 'error': None, 'unAuthorizedRequest': False, '__abp': True}