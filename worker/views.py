from django.shortcuts import render
from.serializers import SignupSerializer,WorkerLoginSerializer,VerifyAccountSerializer,ForgotPasswordSerializer
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .send_sms import send_sms
from rest_framework.exceptions import APIException
from Authority.models import Users
from .models import Worker_details

# Create your views here.

class WorkerSignUpView(GenericAPIView):
    serializer_class=SignupSerializer
    def post(self,request:Request):
        data=request.data
        serializer=self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            try:
                send_sms(data['Worker_details.phone_number'],data['email'])
            except:
                serializer.instance.delete()
                raise APIException('Failed to send otp to your phone. Register again')
            response={
                'status':201,
                'message':'Worker registered successfully,Confrim by entering your Otp',
            }
            return Response(data=response,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class WorkerVerifyotp(APIView):
    serializer_class=VerifyAccountSerializer
    def post(self,request):
        try:
            data=request.data
            serializer=self.serializer_class(data=data)
            if serializer.is_valid():
                phone_number=serializer.data['phone_number']
                otp=serializer.data['otp']
                try:
                    worker=Worker_details.objects.get(phone_number=phone_number)
                    user=worker.worker
                    if not user:
                        response={
                            'status':400,
                            'message':'Invalid Phone number'
                        }
                        return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
                    if user.otp == otp:
                        user.is_verified=True
                        user.otp=None
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
                except Worker_details.DoesNotExist:
                    response = {
                        'status':400,
                        'message': 'Worker not found for the provided phone number'
                    }
                    return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        except:
            response={
                'status':400,
                'message':'Something went wrong'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
    
class WorkerLoginView(GenericAPIView):
    serializer_class=WorkerLoginSerializer
    def post(self,request:Request):
        data=request.data
        serializer=self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        tokens=RefreshToken.for_user(user)
        response={
            'status':200,
            'message':'Worker login successfull',
            'access':str(tokens.access_token),
            'refresh':str(tokens),
        }
        return Response(data=response,status=status.HTTP_200_OK)
    
class ForgotPassword(GenericAPIView):
    serializer_class=ForgotPasswordSerializer
    def patch(self,request):
        data=request.data
        serializer=self.serializer_class(data=data)
        if not serializer.is_valid:
            response={
                'status':400,
                'message':'Something went wrong'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        response={
            'status':200,
            'message':'Otp sent successfully'
        }
        return Response(data=response,status=status.HTTP_200_OK)

class VerifyForgototp(GenericAPIView):
    pass

