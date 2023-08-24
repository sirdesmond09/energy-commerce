import requests
import os

BASE_API_URL = "https://api.flutterwave.com/v3"
FLW_SECRET_KEY=os.getenv('FLW_SECRET_KEY')

def get_banks():
    
    res = requests.get(url= f'{BASE_API_URL}/banks/NG',
                       headers = {
    'Authorization': f'Bearer {FLW_SECRET_KEY}'
    })

    return res.json()



def resolve_account(account_number,bank_code):
    res = requests.post(url = f"{BASE_API_URL}/accounts/resolve",
                       headers={"Authorization":f"Bearer {FLW_SECRET_KEY}"},
                       json={"account_number": account_number,
                             "account_bank": bank_code}
                       )
    
    return res.json()