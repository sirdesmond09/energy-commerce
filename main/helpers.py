import os
import requests
from rest_framework.exceptions import ValidationError

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
    
