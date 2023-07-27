import json
import os
import requests
from rest_framework.exceptions import ValidationError
from django.utils import timezone

from main.helpers.encryption import decrypt_data, encrypt_data
import logging
from config.settings import Common

logging.config.dictConfig(Common.LOGGING)

logger = logging.getLogger('django.server')

def payment_is_verified(trans_id):
    
    """Validate flutterwave payment"""

    
    base_url = os.getenv("FLUTTER_VERIFICATION_URL")
    token = os.getenv("FLW_SECRET_KEY")
    url = base_url + f"{trans_id}/verify/"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    res = requests.get(url, headers=headers)

    logger.warning(f"The response is: {res.content}")
    
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
    
    """Validate the Pay with specta payment on re-query API"""
    
    payload = {
        "purchaseId" : ref
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
    logger.warning(f"PWS: {data}")
    result = data.get("result", None)
    error = data.get("error", None)
    
    if error != None and error.get("code") == 404:
        return False
    elif result!= None and result.get("item1") == True and result.get("item2") == 'Loan booking was sucessful':
        return True
    else:
        return False





def refund(balance):
    
    """Refund the down payment if loan request fails"""
    
    base_url = os.getenv("FLUTTER_VERIFICATION_URL")
    token = os.getenv("FLW_SECRET_KEY")
    url = base_url + f"{balance.transaction_id}/refund/"
    
    header =  {'Authorization': f"Bearer {token}",
               'Content-Type' : 'application/json'
               }
    payload = {
    "amount": balance.paid_amount,
    "comments": "Imperium Refund -- Pay with specta loan failed to complete"
    }
    
    res = requests.post(url=url, json=payload, headers=header)
    logger.warning(f"Refund: {res.json()}")

    if res.json().get("status") == "success":
        return True
    return False

# not found
# {'result': None, 'targetUrl': None, 'success': False, 'error': {'code': 404, 'message': 'Purchase was not found!', 'details': None, 'validationErrors': None}, 'unAuthorizedRequest': False, '__abp': True}

# success
# {'result': {'item1': True, 'item2': 'Loan booking was sucessful'}, 'targetUrl': None, 'success': True, 'error': None, 'unAuthorizedRequest': False, '__abp': True}