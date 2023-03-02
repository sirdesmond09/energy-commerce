from django.test import TestCase

# Create your tests here.


# import requests
# import random


# res = requests.get('https://imperium.herokuapp.com/v1/products/',
#              headers= {'accept': 'application/json',
#                        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc3NzUzNDczLCJqdGkiOiJhZWY3Y2VkOTBiZmQ0MzA4OTZjNjVkYzYwZTVmNTEwMyIsInVzZXJfaWQiOiI1OTEzM2M3ZC03ZWNkLTRkMDgtYjUwOS01YzA5YTFjZTMyYzcifQ.EdaQcHo8FOJ1xei_ZC2kSealH-aeVh7UELc8H1_1mfw'})

# locations = requests.get('https://imperium.herokuapp.com/v1/locations/',
#              headers= {'accept': 'application/json',
#                        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc3NzUzNDczLCJqdGkiOiJhZWY3Y2VkOTBiZmQ0MzA4OTZjNjVkYzYwZTVmNTEwMyIsInVzZXJfaWQiOiI1OTEzM2M3ZC03ZWNkLTRkMDgtYjUwOS01YzA5YTFjZTMyYzcifQ.EdaQcHo8FOJ1xei_ZC2kSealH-aeVh7UELc8H1_1mfw'})
# print(locations)

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


    
    


