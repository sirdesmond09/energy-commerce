import string
import random
import secrets

def generate_password():
    a = []
    for _ in range(3):
        a.append(random.choice(string.ascii_lowercase))
        a.append(random.choice(string.ascii_uppercase))
        a.append(random.choice(string.digits))
        a.append(random.choice(["@","!","$","#"]))
    random.shuffle(a)
    return "".join(a)


def generate_code(n):
    
    alphabet = string.ascii_letters + string.digits
    code = ''.join(secrets.choice(alphabet) for i in range(n))
    return code




def generate_referral_code(length=8):
    characters = string.ascii_letters
    referral_code = ''.join(secrets.choice(characters) for _ in range(length))
    return referral_code
