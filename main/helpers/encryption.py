from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import json
import os

def base64_decoding(input):
    decoded_bytes = base64.b64decode(input)
    return decoded_bytes


PWS_SECRET = base64_decoding(os.getenv('PWS_SECRET'))
PWS_IV = base64_decoding(os.getenv('PWS_IV'))

data = {
    "queryParameters": [
        {
            "parameterName": "spectaID",
            "value": "SPTest"
        }
    ],
    "headers": {
        "x-ApiKey": "TEST_API_KEY"
    },
    "jsonBody": ""
}

def encrypt_data(data):

    # Serialize the data dictionary as JSON and encode as bytes
    data_json = json.dumps(data).encode('utf-8')
    padded_data = pad(data_json, AES.block_size)

    cipher = AES.new(PWS_SECRET, AES.MODE_CBC, PWS_IV)

    ciphertext = cipher.encrypt(padded_data)


    # Encode ciphertext as base64 and obtain a string representation
    ciphertext_base64 = base64.b64encode(ciphertext).decode('utf-8')

    return ciphertext_base64



def decrypt_data(ciphertext_base64):


    cipher = AES.new(PWS_SECRET, AES.MODE_CBC, PWS_IV)

    ciphertext = base64_decoding(ciphertext_base64)

    decrypted_data = cipher.decrypt(ciphertext)

    # Unpad the decrypted data
    unpadded_data = unpad(decrypted_data, AES.block_size)

    return unpadded_data.decode('utf-8')