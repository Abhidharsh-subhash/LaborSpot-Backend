# Download the helper library from https://www.twilio.com/docs/python/install
import random
from twilio.rest import Client
from Authority.models import Users
from decouple import config


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
def send_sms(phone,mail):
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    otp=random.randint(1000,9999)
    phone_number='+91'+phone
    try:
        user=Users.objects.get(is_staff=True,email=mail)
        user.otp=otp
        user.save()
    except Exception as e:
        raise e

    message = client.messages.create(body=f"You verification code for LaborSpot is {otp}",from_='+14066938441',to=phone_number)

    print(message.sid)
    print('message send successfully')