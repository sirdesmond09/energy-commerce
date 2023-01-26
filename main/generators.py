import datetime
import random

def generate_booking_id():
    current_time = datetime.datetime.now()
    booking_id = current_time.strftime('%Y%m%d%H%M%S') + str(random.randint(1000,9999))
    return booking_id