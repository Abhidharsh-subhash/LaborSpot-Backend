from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from.serializers import SignUpSerializer,UserLoginSerializer,VerifyAccountSerializer,UserPrivacySerializer
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
from .emails import send_otp_via_mail

# Create your views here.

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
                'status':201,
                'message':'User registration successfull,check email and verify by otp',
            }
            return Response(data=response,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class UserVerifyotp(APIView):
    serializer_class=VerifyAccountSerializer
    def post(self,request):
        try:
            data=request.data
            serializer=self.serializer_class(data=data)
            if serializer.is_valid():
                email=serializer.data['email']
                otp=serializer.data['otp']
                try:
                    user=Users.objects.get(email=email)
                    if not user:
                        response={
                            'status':400,
                            'message':'Invalid Email address'
                        }
                        return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
                    if user.otp == otp:
                        user.is_verified=True
                        user.save()
                        response={
                            'status':200,
                            'message':'Otp Verified you can login with your credentials'
                        }
                        return Response(data=response,status=status.HTTP_200_OK)
                    else:
                        response={
                            'status':400,
                            'message':'Wrong otp'
                        }
                        return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
                except Users.DoesNotExist:
                    response = {
                        'status':400,
                        'message': 'User not found for the provided email'
                    }
                    return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        except:
            response={
                'status':400,
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
            'status':200,
            'message':'User login successful',
            'access':str(tokens.access_token),
            'refresh':str(tokens)
        }
        return Response(data=response,status=status.HTTP_200_OK)  
    def get(self,request):
        content={
            'status':200,
            'message':'It is for User login only POST request is allowed'
        }
        return Response(data=content,status=status.HTTP_200_OK)
    
class UserPrivacy(GenericAPIView):
    serializer_class=UserPrivacySerializer
    def post(self,request):
        breakpoint()
        # Access the request object from the serializer context
        request = self.context.get('request')
        # Get the current user from the request
        current_user = request.user
        print(current_user)

