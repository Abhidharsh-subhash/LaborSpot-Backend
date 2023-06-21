from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from.serializers import SignUpSerializer,UserLoginSerializer,VerifyAccountSerializer,ForgotPasswordSerializer,SetNewPasswordSerializer,WorkerListSerializer,UserProfileSerializer
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
from .emails import send_otp_via_mail,forgot_send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .permissions import IsUser
from django.db.models import Q

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
        # response = Response(
        #     {
        #         'status': 200,
        #         'message': 'User login successful',
        #         'access': str(tokens.access_token),
        #         'refresh': str(tokens)
        #     },
        #     status=status.HTTP_200_OK
        # )
        response={
            'status':200,
            'message':'User login successful',
            'access':str(tokens.access_token),
            'refresh':str(tokens)
        }
        return Response(data=response,status=status.HTTP_200_OK)
        # Set the cookies
        # response.set_cookie('access_token', tokens.access_token)
        # response.set_cookie('refresh_token', str(tokens))
        # return response
    
class ForgotPasswordEmail(GenericAPIView):
    serializer_class=ForgotPasswordSerializer
    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        email = request.data.get('email', '')
        if Users.objects.filter(email=email).exists():
            user=Users.objects.get(email=email)
            #encoding the user id
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            #the default class will take care of knowing if the user had changed the password that it will invalidated when the user uses it
            token=PasswordResetTokenGenerator().make_token(user)
            current_site=get_current_site(request=request).domain
            relativelink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
            absurl='http://'+current_site+relativelink
            email_body='Hello \n Use below link to change your password \n'+absurl
            data={'email_body':email_body,'to_email':user.email,'email_subject':'Reset your password'}
            forgot_send_mail(data)
            response={
            'status':200,
            'message':'We have send a link to your email to reset your password'
            }
            return Response(data=response,status=status.HTTP_200_OK)
        response={
            'status':400,
            'message':'Invalid mail id'
        }
        return Response(data=response,status=status.HTTP_400_BAD_REQUEST)

class PasswordTokenCheck(GenericAPIView):
    def get(self,request):
        uidb64 = request.data.get('uidb64')
        token = request.data.get('token')
        try:
            id=smart_str(urlsafe_base64_decode(uidb64))
            user=Users.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                response={
                    'status':401,
                    'message':'Toke is not valid request a new one'
                }
                return Response(data=response,status=status.HTTP_401_UNAUTHORIZED)
            response={
                'status':200,
                'success':True,
                'message':'Credentials valid',
                'uidb64':uidb64,
                'token':token
            }
            return Response(data=response,status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user):
                response={
                    'status':401,
                    'message':'Token is not valid request a new one'
                }
                return Response(data=response,status=status.HTTP_401_UNAUTHORIZED)
            
class SetNewPassword(GenericAPIView):
    serializer_class=SetNewPasswordSerializer
    def patch(self,request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response={
            'status':200,
            'message':'Password reset successfully completed',
        }
        return Response(data=response,status=status.HTTP_200_OK)

class WorkerList(GenericAPIView):
    permission_classes=[IsUser]
    serializer_class=WorkerListSerializer
    queryset=Users.objects.filter(Q(is_staff=True) & Q(is_verified=True) & Q(is_active=True)).select_related('worker').all()
    def get(self,request):
        worker_id=request.data.get('worker_id')
        search_param=request.data.get('search')
        if search_param:
            workers=self.queryset.filter(username__icontains=search_param)
            serializer=self.serializer_class(workers,many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        if worker_id is None:
            serializer=self.serializer_class(self.get_queryset(),many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        else:
            worker=get_object_or_404(self.get_queryset(),id=worker_id)
            serializer=self.serializer_class(worker)
            return Response(data=serializer.data,status=status.HTTP_200_OK)

class UserProfileView(APIView):
    permission_classes = [IsUser]
    serializer_class=UserProfileSerializer
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)
    def patch(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response={
                'status' : 200,
                'message':'Your profile updated successfully'
            }
            return Response(data=response,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)