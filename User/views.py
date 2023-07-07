from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from.serializers import SignUpSerializer,UserLoginSerializer,CompleteFeedbackSerializer,BookingHistorySerializer,VerifyAccountSerializer,ForgotPasswordSerializer,SetNewPasswordSerializer,WorkerListSerializer,UserProfileSerializer,UserPrivacySerializer,BookingSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import APIException
# from .emails import send_otp_via_mail
# from django.core.mail import send_mail
import random
from django.conf import settings
from Authority.models import Users,Booking
from .emails import send_otp_via_mail,forgot_send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .permissions import IsUser
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from datetime import datetime
from Worker.models import Worker_details
from datetime import date
from datetime import datetime
import string,secrets
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
        category_id = request.data.get('category_id')
        if search_param:
            workers=self.queryset.filter(Q(username__icontains=search_param) | Q(worker__category__category__icontains=search_param))
            if category_id:  # Apply additional category filtering
                workers = workers.filter(worker__category__id=category_id)
            serializer=self.serializer_class(workers,many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        elif worker_id is None:
            queryset=self.get_queryset()
            if category_id:  # Apply category filtering
                queryset = queryset.filter(worker__category__id=category_id)
            serializer=self.serializer_class(queryset,many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        elif category_id:
            workers = self.queryset.filter(worker__category__id=category_id)
            serializer = self.serializer_class(workers, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
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
    
class UserPrivacy(GenericAPIView):
    permission_classes=[IsUser]
    serializer_class=UserPrivacySerializer
    def patch(self,request):
        user = request.user
        serializer=self.serializer_class(user,data=request.data)
        if serializer.is_valid():
            # Check if the current password provided matches the user's actual password
            current_password=serializer.validated_data.get('password')
            if check_password(current_password,user.password):
                new_password=serializer.validated_data.get('new_password')
                confirm_password=serializer.validated_data.get('confirm_password')
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    response={
                        'status':200,
                        'message':'Your Password Updated successfully'
                    }
                    return Response(data=response,status=status.HTTP_200_OK)
                else:
                    response={
                        'status':400,
                        'message':'New password and confirm password are not matching'
                    }
                    return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
            else:
                response={
                    'status':400,
                    'message':'You have provided the wrong password'
                }
                return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class WorkerBooking(GenericAPIView):
    permission_classes=[IsUser]
    serializer_class=BookingSerializer
    # this method is overridden to remove the 'user' field from the fields dictionary
    def get_fields(self):
        fields = super().get_fields()
        fields.pop('user')
        return fields
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    #method for generating the custom booking number
    def generate_booking_id(self):
        alphabet = string.ascii_letters + string.digits
        code_length = 10
        while True:
            booking_id = ''.join(secrets.choice(alphabet) for _ in range(code_length))
            # Check if the generated booking ID already exists in the database
            if not Booking.objects.filter(booking_id=booking_id).exists():
                return booking_id
            else:
                self.generate_booking_id()
    def post(self, request):
        worker = request.data.get('worker')
        try:
            worker = Users.objects.get(id=worker)
        except Users.DoesNotExist:
            return Response({"error": "Invalid worker."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user=Worker_details.objects.get(worker=worker.id)
            amount=user.charge
        except Users.DoesNotExist:
            return Response({"error": "Invalid worker."}, status=status.HTTP_400_BAD_REQUEST)
        time_from=request.data['time_from']
        time_to=request.data['time_to']
        time_from = datetime.strptime(time_from, "%H:%M").time()
        time_to = datetime.strptime(time_to, "%H:%M").time()
        datetime_from = datetime.combine(datetime.today(), time_from)
        datetime_to = datetime.combine(datetime.today(), time_to)
        duration = datetime_to - datetime_from
        duration_hours = duration.total_seconds() / 3600
        cost=int(amount*duration_hours)
        booking_number=self.generate_booking_id()
        booking_data = {
            'booking_id':booking_number,
            'user': request.user.id,
            'worker': worker.id,
            'date': request.data.get('date'),
            'time_from': request.data.get('time_from'),
            'time_to': request.data.get('time_to'),
            'payment_amount':cost,
            'location': request.data.get('location'),
            'contact_information': request.data.get('contact_information'),
            'instructions': request.data.get('instructions'),
        }
        # Serialize the booking data
        serializer = self.serializer_class(data=booking_data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            response={
                'status':201,
                'message':"Worker booked successfull",
                'wage of the worker':cost,
                'Booking id':booking_number
            }
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(data=response, status=status.HTTP_201_CREATED)
        else:
            response={
                'status':400,
                'message':'Something went wrong. please try again'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        
class BookingHistory(GenericAPIView):
    permission_classes=[IsUser]
    serializer_class=BookingHistorySerializer
    def get(self,request):
        user=request.user.id
        status=request.data.get('status')
        if status is not None:
            bookings=Booking.objects.filter(user=user,status=status)
        else:
            bookings=Booking.objects.filter(user=user)
        serializer=self.serializer_class(bookings,many=True)
        return Response(data=serializer.data)
    def post(self,request):
        user=request.user.id
        booking_id=request.data.get('booking_id')
        reason=request.data.get('reason')
        try:
            booking=Booking.objects.get(user=user,pk=booking_id,status='pending')
        except Booking.DoesNotExist:
            response={
                'status':404,
                'message':'Booking not found or cannot be cancelled.'
            }
            return Response(data=response,status=status.HTTP_404_NOT_FOUND)
        if reason is not None:
            booking.status='cancelled'
            booking.cancellation_reason=reason
            booking.save()
            response={
                'status':200,
                'message':'Booking has been cancelled successfully.'
            }
            return Response(data=response,status=status.HTTP_200_OK)
        else:
            response={
                'status':400,
                'message':'Please provide the reason for cancellation'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)

class CompleteFeedback(GenericAPIView):
    permission_classes=[IsUser]
    serializer_class=CompleteFeedbackSerializer
    def patch(self,request):
        booking_id=request.data.get('booking_id')
        feedback=request.data.get('feedback')
        try:
            booking=Booking.objects.get(pk=booking_id)
        except Booking.DoesNotExist:
            response={
                'status':400,
                'message':'booking_id does not exist'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        if booking.status == 'accepted':
            if feedback is None:
                response={
                    'status':400,
                    'message':'Please provide the feedback before marking it as completed'
                }
                return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
            today=date.today()
            current = datetime.now().strftime('%H:%M:%S')
            current_time = datetime.strptime(current, '%H:%M:%S').time()
            if (booking.date == today) and (current_time >= booking.time_to):
                booking.status='completed'
                booking.feedback=feedback
                booking.save()
                response={
                    'status':200,
                    'message':'Service completed successfully'
                }
                return Response(data=response,status=status.HTTP_200_OK)
            else:
                response={
                    'status':400,
                    'message':'You are trying to complete the wrong work'
                }
                return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        else:
            response={
                'status':400,
                'message':'Having some problem related to booking'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
            