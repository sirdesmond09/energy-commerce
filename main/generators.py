import datetime
import random
import uuid
import string

def generate_booking_id():
    current_time = datetime.datetime.now()
    booking_id = current_time.strftime('%Y%m%d%H%M%S') + str(random.randint(1000,9999))
    return booking_id




def generate_order_id():
    
    """
    Generates a unique and untraceable order ID using a random 8-character string and a random salt.
    """
    salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)) # Generate a random 4-character alphanumeric salt
    order_id = str(uuid.uuid4().int & (1<<32)-1)[:8] # Generate an 8-character alphanumeric string from the first 32 bits of a UUID
    return order_id + salt