from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from User.payments import make_paypal_payment
from.serializers import SignUpSerializer,PaymentSerializer,ResendOtpSerializer,UserLoginSerializer,CompleteFeedbackSerializer,BookingHistorySerializer,VerifyAccountSerializer,ForgotPasswordSerializer,SetNewPasswordSerializer,WorkerListSerializer,UserProfileSerializer,UserPrivacySerializer,BookingSerializer
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
from Worker.models import Worker_details
from datetime import date,datetime,timedelta
from datetime import datetime
from pytz import timezone
import string,secrets
import paypalrestsdk
import pytz
from decouple import config
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
                'message':'User registration successfull,check email and verify by otp',
                'warning':'OTP is valid for only 5 minutes'
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
                user = get_object_or_404(Users, email=email)
                if not user:
                        response={
                            'message':'Invalid Email address'
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
                                'message': 'OTP has expired,You can resend the otp'
                                
                            }
                            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            user.is_verified=True
                            user.otp=None
                            user.otp_expiration=None
                            user.save()
                            response={
                                'message':'Otp Verified you can login with your credentials'
                            }
                            return Response(data=response,status=status.HTTP_200_OK)
                elif user.otp == None:
                        response={
                            'message':'You are already verified'
                        }
                        return Response(data=response,status=status.HTTP_226_IM_USED)
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
        
class ResendOtp(GenericAPIView):
    serializer_class=ResendOtpSerializer
    def post(self,request):
        data=request.data
        serializer=self.serializer_class(data=data)
        if serializer.is_valid():
            email=serializer.data['email']
            user=get_object_or_404(Users,email=email)
            try:  
                send_otp_via_mail(email)
            except:
                raise APIException('Failed to send otp to mail.Try again')
            response={
                'message':'Resend otp successfull',
                'warning':'OTP is valid for only 5 minutes'
            }  
            return Response(data=response,status=status.HTTP_200_OK)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
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
        if Users.objects.filter(email=email,is_user=1).exists() and serializer.is_valid():
            user=Users.objects.get(email=email)
            #encoding the user id
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            #the default class will take care of knowing if the user had changed the password that it will invalidated when the user uses it
            token=PasswordResetTokenGenerator().make_token(user)
            current_site=get_current_site(request=request).domain
            relativelink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
            redirect_url = request.data.get('redirect_url', '')
            absurl='http://'+current_site+relativelink
            email_body='Hello \n Use below link to change your password \n'+absurl+"?redirect_url="+redirect_url
            data={'email_body':email_body,'to_email':user.email,'email_subject':'Reset your password'}
            forgot_send_mail(data)
            response={
            'status':200,
            'message':'We have send a link to your email to reset your password'
            }
            return Response(data=response,status=status.HTTP_200_OK)
        response={
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
                    'message':'Toke is not valid request a new one'
                }
                return Response(data=response,status=status.HTTP_401_UNAUTHORIZED)
            response={
                'success':True,
                'message':'Credentials valid',
                'uidb64':uidb64,
                'token':token
            }
            return Response(data=response,status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user):
                response={
                    'message':'Token is not valid request a new one'
                }
                return Response(data=response,status=status.HTTP_401_UNAUTHORIZED)
            
class SetNewPassword(GenericAPIView):
    serializer_class=SetNewPasswordSerializer
    def patch(self,request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response={
            'message':'Password reset successfully completed',
        }
        return Response(data=response,status=status.HTTP_200_OK)

class WorkerList(GenericAPIView):
    permission_classes=[IsUser]
    serializer_class=WorkerListSerializer
    queryset=Users.objects.filter(Q(is_staff=True) & Q(is_verified=True) & Q(is_active=True)).select_related('worker').all()
    def get(self,request):
        search_param=request.data.get('search')
        category_id = request.data.get('category_id')
        order_by = request.data.get('order_by')
        if category_id and search_param:
            workers=self.queryset.filter(Q(username__icontains=search_param) & Q(worker__category__id=category_id))
            if order_by == 'high_to_low':
                workers = workers.order_by('-worker__charge')
            elif order_by == 'low_to_high':
                workers = workers.order_by('worker__charge') 
            if workers.exists():
                serializer=self.serializer_class(workers,many=True)
                return Response(data=serializer.data,status=status.HTTP_200_OK)
            else:
                response={
                    'message':'No data found'
                }
                return Response(data=response,status=status.HTTP_404_NOT_FOUND)
        elif search_param:
            workers=self.queryset.filter(Q(username__icontains=search_param) | Q(worker__category__category__icontains=search_param))
            if order_by == 'high_to_low':
                workers = workers.order_by('-worker__charge') 
            elif order_by == 'low_to_high':
                workers = workers.order_by('worker__charge') 
            if workers.exists():
                serializer=self.serializer_class(workers,many=True)
                return Response(data=serializer.data,status=status.HTTP_200_OK)
            else:
                response={
                    'message':'No data found'
                }
                return Response(data=response,status=status.HTTP_404_NOT_FOUND)
        elif category_id:
            workers = self.queryset.filter(worker__category__id=category_id)
            if order_by == 'high_to_low':
                workers = workers.order_by('-worker__charge') 
            elif order_by == 'low_to_high':
                workers = workers.order_by('worker__charge') 
            if workers.exists():
                serializer = self.serializer_class(workers, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                response={
                    'message':'No data found'
                }
                return Response(data=response,status=status.HTTP_404_NOT_FOUND)
        elif order_by:
            if order_by == 'high_to_low':
                workers = self.queryset.order_by('-worker__charge') 
            elif order_by == 'low_to_high':
                workers = self.queryset.order_by('worker__charge')
            if workers.exists():
                serializer = self.serializer_class(workers, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                response={
                    'message':'No data found'
                }
                return Response(data=response,status=status.HTTP_404_NOT_FOUND)
        else:
            workers=self.get_queryset()
            if workers.exists():
                serializer=self.serializer_class(workers,many=True)
                return Response(data=serializer.data,status=status.HTTP_200_OK)
            else:
                response={
                    'message':'No data found'
                }
                return Response(data=response,status=status.HTTP_404_NOT_FOUND)

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
                        'message':'Your Password Updated successfully'
                    }
                    return Response(data=response,status=status.HTTP_200_OK)
                else:
                    response={
                        'message':'New password and confirm password are not matching'
                    }
                    return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
            else:
                response={
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
    def get_next_available_time(self, worker_id, start_time):
        today = datetime.now().date()
        current = start_time.date()
        x=current.strftime('%Y-%m-%d')
        current_day=datetime.strptime(x, '%Y-%m-%d').date()
        current_time = start_time.time()

        while current_day <= today:
            now = datetime.now()
            current_datetime = datetime.combine(current_day, current_time)
            if current_day == today and current_datetime <= now:
                # Skip past time that has already passed today
                current_datetime = now + timedelta(minutes=30)
            if current_datetime.time() >= datetime.strptime('08:00', '%H:%M').time():
                # Check if the time slot is available
                existing_bookings = Booking.objects.filter(
                    worker_id=worker_id,
                    date=current_day,
                    time_to__gte=current_datetime.time()
                )
                if not existing_bookings.exists():
                    return current_datetime
            
            # Increment the time by 30 minutes
            current_time += timedelta(minutes=30)
            if current_time >= datetime.strptime('23:30', '%H:%M').time():
                # If the time exceeds 23:30, move to the next day
                current_day += timedelta(days=1)
                current_time = datetime.strptime('08:00', '%H:%M').time()

        return None
    def post(self, request):
        worker = request.data.get('worker')
        try:
            worker = Users.objects.get(id=worker,is_staff=True)
        except Users.DoesNotExist:
            return Response({"error": "Invalid worker."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            breakpoint()
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
         # Check if the user has any bookings at the requested time slot
        existing_bookings = Booking.objects.filter(
            user=request.user,
            date=request.data.get('date'),
            time_to__gte=datetime_from,
            time_from__lte=datetime_to
        )
        # if existing_bookings.exists():
        #     response={
        #         'status':226,
        #         'message':'Time slot is not available.Please try a different time for the worker that you are looking for.'
        #     }
        #     return Response(data=response, status=status.HTTP_226_IM_USED)
        if existing_bookings.exists():
            next_available_time = self.get_next_available_time(worker.id, datetime_from)
            if next_available_time:
                response = {
                    'message': 'Time slot is not available. Next available time slot: {}'.format(next_available_time),
                }
            else:
                response = {
                    'message': 'Time slot is not available. No further available time slots.',
                }
            return Response(data=response, status=status.HTTP_226_IM_USED)

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
        if bookings.exists():
            serializer=self.serializer_class(bookings,many=True)
            return Response(data=serializer.data)
        response={
            'message':'No data found'
        }
        return Response(data=response)
    def post(self,request):
        user=request.user.id
        booking_id=request.data.get('booking_id')
        reason=request.data.get('reason')
        try:
            booking=Booking.objects.get(user=user,pk=booking_id,status='pending')
        except Booking.DoesNotExist:
            response={
                'message':'Booking not found or cannot be cancelled.'
            }
            return Response(data=response,status=status.HTTP_404_NOT_FOUND)
        if reason is not None:
            booking.status='cancelled'
            booking.cancellation_reason=reason
            booking.save()
            response={
                'message':'Booking has been cancelled successfully.'
            }
            return Response(data=response,status=status.HTTP_200_OK)
        else:
            response={
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
                'message':'booking_id does not exist'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        if booking.status == 'accepted':
            if feedback is None:
                response={
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
                    'message':'Service completed successfully'
                }
                return Response(data=response,status=status.HTTP_200_OK)
            else:
                response={
                    'message':'You are trying to complete the wrong work'
                }
                return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        else:
            response={
                'message':'Having some problem related to booking'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
     
class Makepayment(GenericAPIView):
    permission_classes=[IsUser]
    serializer_class=PaymentSerializer
    def post(self,request):
        user=request.user.id
        booking_id=request.data.get('booking_id')
        wage=request.data.get('wage')
        try:
            booking=Booking.objects.get(user=user,booking_id=booking_id)
        except Booking.DoesNotExist:
            response={
                'messsage':'Booking id not found'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        if booking.payment_amount != int(wage):
            response={
                'message':'Incorrect payment amount provided'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        elif booking.payment_status == 'completed':
            response={
                'message':'Payment already completed'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        elif booking.status == 'cancelled' or booking.status == 'terminated':
            response={
                'message':'Booking already cancelled'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        elif booking.status == 'pending':
            response={
                'message':'Payment can be done only after the work is completed'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        paypalrestsdk.configure(
            {
                'mode': config('mode'),
                'client_id': config('client_id'),
                'client_secret': config('client_secret'),
            }
        )  
        paypal_payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [
                {
                    "amount": 
                    {
                        "total": int(booking.payment_amount),
                        "currency": "USD"
                    },
                "description": "Payment for booking #" + str(booking_id),"invoice_number": str(booking_id)}],
                 "redirect_urls": {
                "return_url": "https://www.sandbox.paypal.com/signin",
                "cancel_url": "http://your-website.com/cancel"
            }
        })

        if paypal_payment.create():
            # booking.payment_status = 'completed'  # Update the payment status
            # booking.save()
            print(paypal_payment)
            approval_url = next(link.href for link in paypal_payment.links if link.rel == 'approval_url')
            response = {
                'approval_url': approval_url
            }
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                'message': 'Failed to create PayPal payment'
            }
            return Response(data=paypal_payment.error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentConfirmation(APIView):
    """
    Endpoint to confirm PayPal payment status
    """
    permission_classes=[IsUser]
    def post(self, request):
        payment_id = request.data.get('payment_id')
        payer_id = request.data.get('payer_id')

        # Use the payment_id and payer_id to confirm the payment status with PayPal
        paypalrestsdk.configure(
            {'mode': config('mode'),
             'client_id': config('client_id'),
             'client_secret': config('client_secret'),
            }
        )
        paypal_payment = paypalrestsdk.Payment.find(payment_id)
        if paypal_payment.execute({"payer_id": payer_id}):
            # Payment is confirmed, update the payment status in your system
            # You can retrieve the corresponding booking and update the payment status
            booking = Booking.objects.get(booking_id=paypal_payment.transactions[0].invoice_number)
            booking.payment_status = 'completed'
            booking.save()

            response = {
                'message': 'Payment confirmed'
            }
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            # Payment confirmation failed
            response = {
                'message': 'Payment confirmation failed'
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
       
        
            