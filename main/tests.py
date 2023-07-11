# from django.test import TestCase

# Create your tests here.


# import requests
# import random

# def generate_order_id():
    
#     """
#     Generates a unique and untraceable order ID using a random 8-character string and a random salt.
#     """
#     salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)) # Generate a random 4-character alphanumeric salt
#     order_id = str(uuid.uuid4().int & (1<<32)-1)[:8] # Generate an 8-character alphanumeric string from the first 32 bits of a UUID
#     return order_id + salt


# res = requests.get('https://imperium.herokuapp.com/v1/orders/',
#              headers= {'accept': 'application/json',
#                        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc4MDg5OTEyLCJqdGkiOiIxNzYzOWY0YjYyN2Y0NDYxODY3OGE1MTBmNjc1ZGNhNiIsInVzZXJfaWQiOiJhYWI4MGY5Yy1jMWYyLTQ0NDUtYjljNS05OWVhNDRjYzFkMzEifQ.51GiGLtCBIa48PUul3TVUppt19_1TNeGM4BGsi2Digg'})

# orders = requests.patch(f'https://imperium.herokuapp.com/v1/orders/{}',
#              headers= {'accept': 'application/json',
#                        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc4MDg5OTEyLCJqdGkiOiIxNzYzOWY0YjYyN2Y0NDYxODY3OGE1MTBmNjc1ZGNhNiIsInVzZXJfaWQiOiJhYWI4MGY5Yy1jMWYyLTQ0NDUtYjljNS05OWVhNDRjYzFkMzEifQ.51GiGLtCBIa48PUul3TVUppt19_1TNeGM4BGsi2Digg'})

# for data in res.json():
#     id = data["id"]
    
#     response = requests.patch(url= f'https://imperium.herokuapp.com/v1/products/{id}/',
#         data= {"locations": [random.choice(locations.json())["id"] for _ in range(5)],
#                "SE_delivery_fee": random.choice(range(3000,5000)),
#                 "SW_delivery_fee": random.choice(range(3000,5000)),
#                 "SS_delivery_fee": random.choice(range(3000,5000)),
#                 "NE_delivery_fee": random.choice(range(3000,5000)),
#                 "NW_delivery_fee": random.choice(range(3000,5000)),
#                 "NC_delivery_fee": random.choice(range(3000,5000)),},
#         headers= {'accept': 'application/json',
#                        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc3NzUzNDczLCJqdGkiOiJhZWY3Y2VkOTBiZmQ0MzA4OTZjNjVkYzYwZTVmNTEwMyIsInVzZXJfaWQiOiI1OTEzM2M3ZC03ZWNkLTRkMDgtYjUwOS01YzA5YTFjZTMyYzcifQ.EdaQcHo8FOJ1xei_ZC2kSealH-aeVh7UELc8H1_1mfw'}
#     )
        
#     print(res.status_code)


    
    
# from Crypto.Cipher import AES
# import base64

# key = bytes("72hu8A8GlK0wCkdQfac83AuPMOqmtKYmFXbNTD9SH1Y=", "utf-8")
# iv = bytes("7EhddMLWwvlqPrMyCYf+VQ==", "utf-8")

# def base64Encoding(input):
#     dataBase64 = base64.b64encode(input)
#     dataBase64P = dataBase64.decode("UTF-8")
#     print(dataBase64, dataBase64P)
#     return dataBase64


# cipher = AES.new(base64Encoding(key), AES.MODE_CBC, iv=base64Encoding(iv))

# print(cipher)


# from Crypto.Cipher import AES
# import base64

# key_base64 = "72hu8A8GlK0wCkdQfac83AuPMOqmtKYmFXbNTD9SH1Y="
# iv_base64 = "7EhddMLWwvlqPrMyCYf+VQ=="

# def base64_decoding(input):
#     decoded_bytes = base64.b64decode(input)
#     return decoded_bytes

# key = base64_decoding(key_base64)
# iv = base64_decoding(iv_base64)

# data = {
#      "queryParameters": [
#          {
#              "parameterName": "spectaID",
#              "value": "SPTest333"
#          }
#      ],
#      "headers": {
#          "x-ApiKey": "TEST_API_KEY"
#      },
#      "jsonBody": ""
# }

# # def base64Encoding(input):
# #     dataBase64 = base64.b64encode(input)
# #     dataBase64P = dataBase64.decode("UTF-8")
# #     return dataBase64

# cipher = AES.new(key, AES.MODE_CBC, iv)

# print(cipher.encrypt(data))




from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import json

key_base64 = "72hu8A8GlK0wCkdQfac83AuPMOqmtKYmFXbNTD9SH1Y="
iv_base64 = "7EhddMLWwvlqPrMyCYf+VQ=="

def base64_decoding(input):
    decoded_bytes = base64.b64decode(input)
    return decoded_bytes


def encrypt_data(data):
    key = base64_decoding(key_base64)
    iv = base64_decoding(iv_base64)

    data_json = json.dumps(data).encode('utf-8')

    # Pad the data to a multiple of the AES block size
    padded_data = pad(data_json, AES.block_size)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(padded_data)

    # Encode ciphertext as base64 and obtain a string representation
    ciphertext_base64 = base64.b64encode(ciphertext).decode('utf-8')

    return ciphertext_base64

#Get OTP data
data1 = {
     "queryParameters": [
         {
             "parameterName": "spectaID",
             "value": "SP528175288"
         }
     ],
     "headers": {
         "x-ApiKey": "9a538cfcb6ad43c8939ac7b55e786bf7"
     },
     "jsonBody": ""
 }


# get eligibility
payload1 = {
    "totalPurchaseAmount": 50000,
    "description": "Payment for items in cart",
    "reference": "2b1a8e1e-oop2-1334-9bq7-dbc79d289396",
    "spectaId": "SP528175288",
    "equityContribution": 0,
    "loanTenorInMonths": 7,
    "otp": "122333",
    "merchantId":"60170"
}

data2 = {
    "queryParameters": [],
    "headers": {
        "x-ApiKey": "9a538cfcb6ad43c8939ac7b55e786bf7"
    },
    "jsonBody": json.dumps(payload1)
}


#validate response
payload2 = {

    "reference": "2b1a8e1e-oop2-1334-9bq7-dbc79d289396"
}

data3 = {
    "queryParameters": [],
    "headers": {
        "x-ApiKey": "9a538cfcb6ad43c8939ac7b55e786bf7"
    },
    "jsonBody": json.dumps(payload2)
}




def decrypt_data(ciphertext_base64):
    key = base64_decoding(key_base64)
    iv = base64_decoding(iv_base64)

    cipher = AES.new(key, AES.MODE_CBC, iv)

    ciphertext = base64_decoding(ciphertext_base64)

    decrypted_data = cipher.decrypt(ciphertext)

    # Unpad the decrypted data
    unpadded_data = unpad(decrypted_data, AES.block_size)

    return unpadded_data.decode('utf-8')




# print(encrypt_data(data2))
print(json.loads(decrypt_data("GYdZxBN120RG8AD7SOPd37PaWjIKue26iW2awQg6axk6umlBZblTz3Yl0I4xPk6h7iInKAVBuGHet6G3EYh0wSCn0BeQeFETIyxYq+U9vrJWx03hkmQp0pQNbdq5CMry6ziHauh4mYHuQhdbQIuLMfPpHXOPLbynlJGpcMlTlnqyIJj6A2mwyr3vD7QqpIpk7qkeZBAQrzZ0Z7TrgoH/rQ==")))



