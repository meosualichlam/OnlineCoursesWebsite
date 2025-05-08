# from multiprocessing.managers import public_methods

from intasend import APIService

API_PUBLISHABLE_KEY = 'ISPubKey_test_d32402bd-a96c-4c4e-8b9f-033d62e41ae0'

API_TOKEN = 'ISSecretKey_test_887ede72-ec20-4758-a77f-4bb48ec8947e'

service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
create_order = service.collect.mpesa_stk_push(phone_number='254712345678', email='test@gmail.com',amount=100, narrative='Purchase of Items')

print(create_order)