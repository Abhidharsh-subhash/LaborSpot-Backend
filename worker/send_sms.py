import requests
import random
from Authority.models import Users 
from decouple import config

def send_sms(phone,email):
    otp_sent = random.randint(1001, 9999)
    try:
        worker=Users.objects.get(is_staff=True,email=email)
        worker.otp=otp_sent
        worker.save()
    except:
        raise Exception('User not found')
    url = 'https://www.fast2sms.com/dev/bulkV2'
    payload = f'variables_values={otp_sent}&route=otp&numbers={phone}'
    authorization_token = config('AUTHORIZATION_TOKEN')
    headers = {
        'authorization': authorization_token,
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
        }
    print(otp_sent)
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)