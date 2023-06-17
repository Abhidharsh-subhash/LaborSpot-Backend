from django.shortcuts import render
from.serializers import SignupSerializer,WorkerLoginSerializer,VerifyAccountSerializer
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
                'message':'Worker registered successfully,Confrim by entering your Otp',
            }
            return Response(data=response,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request:Request):
        content={
            'message':'It is for Worker signup only POST request is allowed'
        }
        return Response(data=content,status=status.HTTP_200_OK)
    
class WorkerVerifyotp(APIView):
    serializer_class=VerifyAccountSerializer
    def post(self,request):
        try:
            data=request.data
            serializer=self.serializer_class(data=data)
            if serializer.is_valid():
                phone_number=serializer.data['phone_number']
                otp=serializer.data['otp']
                worker=Worker_details.objects.get(phone_number=phone_number)
                user=worker.worker
                if not user:
                    response={
                        'message':'Invalid Phone number'
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
    
class WorkerLoginView(GenericAPIView):
    serializer_class=WorkerLoginSerializer
    def post(self,request:Request):
        data=request.data
        serializer=self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        tokens=RefreshToken.for_user(user)
        response={
            'message':'Worker login successfull',
            'access':str(tokens.access_token),
            'refresh':str(tokens),
        }
        return Response(data=response,status=status.HTTP_200_OK)
    def get(self,request):
        response={
            'message':'It is for Worker login only Post request is allowed'
        }
        return Response(data=response,status=status.HTTP_200_OK)
