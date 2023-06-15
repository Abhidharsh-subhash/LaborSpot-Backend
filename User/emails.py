from django.core.mail import send_mail
import random
from django.conf import settings
from Authority.models import Users

def send_otp_via_mail(email):
    if email:
        subject='Your account verification mail'
        otp=random.randint(1000,9999)
        message=f'Your otp is {otp}'
        email_from=settings.EMAIL_HOST_USER
        send_mail(subject,message,email_from,[email])
        user_obj=Users.objects.get(email=email)
        user_obj.otp=otp
        user_obj.save()
        print('email send successfully')
    else:
        print('error at send_otp_via_mail')