from django.shortcuts import render
from.serializers import SignupSerializer,ResendOtpSerializer,WorkerLoginSerializer,VerifyAccountSerializer,ForgotPasswordSerializer,WorkerProfileSerializer,BookingSerializer,WorkerPrivacySerializer,VerifyForgotchangeserializer
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
from .permissions import IsWorker
from django.contrib.auth.hashers import check_password
from Authority.models import Booking
from Chat.models import chatroom
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from pytz import timezone
import pytz

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
                'warning':'OTP is valid only for 5 minutes'
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
                    elif user.otp == otp:
                        otp_expiration_utc = user.otp_expiration
                        kolkata_timezone = pytz.timezone('Asia/Kolkata')
                        otp_expiration_kolkata = otp_expiration_utc.astimezone(kolkata_timezone)
                        # otp_expiration_utc = user.otp_expiration.astimezone(timezone('UTC'))
                        current = datetime.now(timezone('Asia/Kolkata'))
                        expiration_time=otp_expiration_kolkata.strftime('%H:%M:%S')
                        current_time=current.strftime('%H:%M:%S')
                        current_date= current.date()
                        expiration_date=otp_expiration_kolkata.date()
                        if current_date >= expiration_date and  expiration_time < current_time:
                            response = {
                                'status': 400,
                                'message': 'OTP has expired,You can resend the otp',
                                'expiration':expiration_time,
                                'currrent':current_time
                            }
                            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            user.is_verified=True
                            user.otp=None
                            user.otp_expiration=None
                            user.save()
                            response={
                                'status':200,
                                'message':'Otp Verified you can login with your credentials'
                            }
                            return Response(data=response,status=status.HTTP_200_OK)
                    elif user.otp == None:
                        response={
                            'status':226,
                            'message':'You are already verified'
                        }
                        return Response(data=response,status=status.HTTP_226_IM_USED)
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
        
class ResendOtp(GenericAPIView):
    serializer_class=ResendOtpSerializer
    def post(self,request):
        data=request.data
        serializer=self.serializer_class(data=data)
        if serializer.is_valid():
            phone_number=serializer.data['phone_number']
            worker=get_object_or_404(Worker_details,phone_number=phone_number)
            user = get_object_or_404(Worker_details.objects.prefetch_related('worker'),phone_number=phone_number)
            breakpoint()
            try:
                send_sms(phone_number,user.worker.email)
            except:
                raise APIException('Failed to send otp to your phone. Try again')
            response={
                'status':200,
                'message':'Otp resend successfull',
                'warning':'OTP is valid for only 5 minutes'
            }
            return Response(data=response,status=status.HTTP_200_OK)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
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
        if serializer.is_valid():
            response={
            'status':200,
            'message':'Otp sent successfully.You can change the password using the otp.'
            }
            return Response(data=response,status=status.HTTP_200_OK)
        else:
            response={
                'status':400,
                'message':'Something went wrong'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)

class VerifyForgototpandchange(GenericAPIView):
    permission_classes=[IsWorker]
    serializer_class=VerifyForgotchangeserializer
    def patch(self,request):
        data=request.data
        if not bool(data):
            response={
                'status':400,
                'message':'Please provide the credentials.'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        serializer=self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            response={
                'status':200,
                'message':'otp verified and password updated successfully'
            }
            return Response(data=response,status=status.HTTP_200_OK)
        else:
            response={
                'status':400,
                'message':'Please try again'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)

class WorkerProfile(APIView):
    permission_classes = [IsWorker]
    serializer_class=WorkerProfileSerializer
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
    
class WorkerPrivacy(GenericAPIView):
    permission_classes=[IsWorker]
    serializer_class=WorkerPrivacySerializer
    def patch(self,request):
        worker=request.user
        serializer=self.serializer_class(worker,data=request.data)
        if serializer.is_valid():
            current_password=serializer.validated_data.get('password')
            if check_password(current_password,worker.password):
                new_password=serializer.validated_data.get('new_password')
                confirm_password=serializer.validated_data.get('confirm_password')
                if new_password == confirm_password:
                    worker.set_password(new_password)
                    worker.save()
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

class WorkRequests(GenericAPIView):
    permission_classes=[IsWorker]
    serializer_class=BookingSerializer
    def get(self,request):
        status=request.data.get('status')
        if status is not None:
            worker=request.user.id
            bookings=Booking.objects.filter(worker=worker,status=status)
            if not bookings:
                response={
                    'status':404,
                    'message':'Not found'
                }
                return Response(data=response)
            serializer=self.serializer_class(bookings,many=True)
            return Response(data=serializer.data)
        else:
            response={
                'status':400,
                'message':'Please provide the status to be filtered'
            }
            return Response(data=response)
    def patch(self,request):
        booking_id=request.data.get('booking_id')
        status=request.data.get('status')
        worker=request.user.id
        try:
            booking=Booking.objects.get(id=booking_id,status='pending')
        except Booking.DoesNotExist:
            response={
                'status':400,
                'message':'Incorrect booking or Requested booking cant perform this action'
            }
            return Response(data=response)
        if status == 'accept':
            booking.status='accepted'
            booking.save()
            chat_room,created = chatroom.objects.get_or_create(name=booking.booking_id)
            # if created:
            #     admin=Users.objects.get(is_superuser=True)
            #     chat_room.users.add(admin.id)
            #     chat_room.users.add(worker)
            response={
            'status':201,
            'message':'Work accepted successfully'
            }
            return Response(data=response)
        elif status == 'reject':
            reason=request.data.get('reason')
            if reason is not None:
                booking.cancellation_reason=reason
                booking.payment_status='cancelled'
                booking.status='rejected'
                booking.save()
                response={
                'status':201,
                'message':'Work rejected successfully'
                }
                return Response(data=response)
            else:
                response={
                    'status':400,
                    'message':'Please provide the reason to reject the booking'
                }
                return Response(data=response)
        else:
            response={
                'status':400,
                'message':'Please provide a valid status'
            }
            return Response(data=response)
        
