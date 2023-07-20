import random
from django.conf import settings
from Authority.models import Users
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from datetime import datetime, timedelta
from pytz import timezone

# def send_otp_via_mail(email):
#     if email:
#         subject='Your account verification mail'
#         otp=random.randint(1000,9999)
#         message=f'Your otp is {otp}'
#         email_from=settings.EMAIL_HOST_USER
#         send_mail(subject,message,email_from,[email])
#         user_obj=Users.objects.get(email=email)
#         user_obj.otp=otp
#         user_obj.save()
#         print('email send successfully')
#     else:
#         print('error at send_otp_via_mail')

def send_otp_via_mail(email):
    if email:
        otp=random.randint(1000,9999)
        user_obj=Users.objects.get(email=email)
        html_template = 'useremail.html'
        mydict = {
            'username': user_obj.username,
            'otp':otp
        }
        html_message = render_to_string(html_template,{'mydict':mydict})
        subject='Welcome to LaborSpot'
        # message=f'Your otp is {otp}'
        # email_from=settings.EMAIL_HOST
        email_from=settings.EMAIL_HOST_USER
        message=EmailMessage(subject, html_message,email_from, [email])
        # send_mail(subject,html_message,email_from,[email])
        message.content_subtype = 'html'
        message.send()
        user_obj.otp=otp
        user_obj.otp_expiration = datetime.now(timezone('Asia/Kolkata')) + timedelta(minutes=5)  # Set expiration to 5 minutes from now
        user_obj.save()
        print(otp)
        print('email send successfully')
    else:
        print('error at send_otp_via_mail')

def forgot_send_mail(data):
    email=EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        to=[data['to_email']]
    )
    email.send()
