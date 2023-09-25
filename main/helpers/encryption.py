from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import json
import os
from cryptography.fernet import Fernet
from config.settings import Common

def base64_decoding(input):
    decoded_bytes = base64.b64decode(input)
    return decoded_bytes


PWS_SECRET = base64_decoding(os.getenv('PWS_SECRET'))
PWS_IV = base64_decoding(os.getenv('PWS_IV'))


ENCRYPTION_SECRET = base64_decoding(os.getenv('ENCRYPTION_SECRET'))
ENCRYPTION_IV = base64_decoding(os.getenv('ENCRYPTION_IV'))


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



class JsonEncryptor:
    
    def __init__(self, secret_key, iv):
        self.secret_key = secret_key
        self.iv = iv
        # print(self.secret_key)
        # print(self.iv)
    

    def encrypt(self,data):
        # print(self.secret_key, self.iv)
        # Serialize the data dictionary as JSON and encode as bytes
        data_json = json.dumps(data).encode('utf-8')
        padded_data = pad(data_json, AES.block_size)

        cipher = AES.new(self.secret_key, AES.MODE_CBC, self.iv)

        ciphertext = cipher.encrypt(padded_data)


        # Encode ciphertext as base64 and obtain a string representation
        ciphertext_base64 = base64.b64encode(ciphertext).decode('utf-8')

        return ciphertext_base64



    def decrypt(self, ciphertext_base64):


        cipher = AES.new(self.secret_key, AES.MODE_CBC, self.iv)

        ciphertext = base64_decoding(ciphertext_base64)

        decrypted_data = cipher.decrypt(ciphertext)

        # Unpad the decrypted data
        unpadded_data = unpad(decrypted_data, AES.block_size)

        return unpadded_data.decode('utf-8')
    



class PasswordEncryptor:
    def __init__(self, secret_key, iv):
        self.secret_key = secret_key
        self.iv = iv

    @staticmethod
    def base64_decoding(input):
        decoded_bytes = base64.b64decode(input)
        return decoded_bytes

    def encrypt(self, plaintext):
        cipher = AES.new(self.secret_key, AES.MODE_CBC, self.iv)
        plaintext_bytes = plaintext.encode('utf-8')
        padded_data = pad(plaintext_bytes, AES.block_size)
        
        ciphertext = cipher.encrypt(padded_data)
        ciphertext_base64 = base64.b64encode(ciphertext).decode('utf-8')

        return ciphertext_base64

    def decrypt(self, ciphertext_base64):
        cipher = AES.new(self.secret_key, AES.MODE_CBC, self.iv)
        ciphertext = self.base64_decoding(ciphertext_base64)

        decrypted_data = cipher.decrypt(ciphertext)
        unpadded_data = unpad(decrypted_data, AES.block_size)

        return unpadded_data.decode('utf-8')
    


password_encryptor = PasswordEncryptor(PWS_SECRET, PWS_IV)
data_encryptor = JsonEncryptor(secret_key=ENCRYPTION_SECRET, iv=ENCRYPTION_IV)
# print(data_encryptor.secret_key)
# print(data_encryptor.iv)