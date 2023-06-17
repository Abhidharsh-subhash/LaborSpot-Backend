from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from.serializers import SignUpSerializer,UserLoginSerializer,VerifyAccountSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import APIException
# from .emails import send_otp_via_mail
# from django.core.mail import send_mail
import random
from django.conf import settings
from Authority.models import Users
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

# Create your views here.

def send_otp_via_mail(email):
    if email:
        user=Users.objects.get(email=email)
        otp=random.randint(1000,9999)
        html_template = 'useremail.html'
        mydict = {
            'username': user.username,
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
        user.otp=otp
        user.save()
        print('email send successfully')
    else:
        print('error at send_otp_via_mail')

class UserSignUpView(GenericAPIView):
    serializer_class=SignUpSerializer
    def post(self,request:Request):
        data=request.data
        serializer=self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            try:
                send_otp_via_mail(data['email'])
            except:
                serializer.instance.delete()
                raise APIException('Failed to send otp mail. Register again')
            response={
                'message':'User registration successfull,check email and verify by otp',
            }
            return Response(data=response,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request:Request):
        content={
            'message':'It is for User signup only POST request is allowed'
        }
        return Response(data=content,status=status.HTTP_200_OK)
    
class UserVerifyotp(APIView):
    serializer_class=VerifyAccountSerializer
    def post(self,request):
        try:
            data=request.data
            serializer=self.serializer_class(data=data)
            if serializer.is_valid():
                email=serializer.data['email']
                otp=serializer.data['otp']
                user=Users.objects.get(email=email)
                if not user:
                    response={
                        'message':'Invalid Email address'
                    }
                    return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
                if user.otp == otp:
                    user.is_verified=True
                    user.save()
                    response={
                        'message':'Otp Verified you can login with your credentials'
                    }
                    return Response(data=response,status=status.HTTP_200_OK)
                else:
                    response={
                        'message':'Wrong otp'
                    }
                    return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        except:
            response={
                'message':'Something went wrong'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    serializer_class=UserLoginSerializer
    def post(self,request:Request):
        data=request.data
        serializer=self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        tokens=RefreshToken.for_user(user)
        response={
                'message':'User login successful',
                'access':str(tokens.access_token),
                'refresh':str(tokens)
            }
        return Response(data=response,status=status.HTTP_200_OK)  
    def get(self,request):
        content={
            'message':'It is for User login only POST request is allowed'
        }
        return Response(data=content,status=status.HTTP_200_OK)
