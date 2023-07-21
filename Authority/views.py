from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from Chat.models import chatroom
from .models import Users, Job_Category, Booking
from .permissions import IsAuthority
from .serializers import UserSerializer, CategorySerializer, WorkerSerializer, LoginSerializer, BookingSerializer, \
    PrivacySerializer


# Create your views here.

class AuthorityLoginApiview(APIView):
    serializer_class = LoginSerializer
    def post(self, request: Request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            response = {
                'status': 400,
                'message': 'Invalid email or password'
            }
            return Response(data=response, status=status.HTTP_401_UNAUTHORIZED)
        elif not (user.is_superuser and user.is_verified):
            response = {
                'status': 400,
                'message': 'You are not authorized to perform this action'
            }
            return Response(data=response, status=status.HTTP_401_UNAUTHORIZED)
        else:
            tokens = RefreshToken.for_user(user)
            response = {
                'status': 200,
                'message': 'Authority Login successfully',
                'access': str(tokens.access_token),
                'refresh': str(tokens)
            }
            return Response(data=response, status=status.HTTP_200_OK)


class AuthorityLogoutView(APIView):
    permission_classes = [IsAuthority]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token_object = RefreshToken(refresh_token)
            token_object.blacklist()
            response = {
                'status': 200,
                'message': 'Authority logged out successfully'
            }
            return Response(data=response, status=status.HTTP_200_OK)
        except:
            response = {
                'status': 400,
                'message': 'Authority logout failed'
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


class CategoryView(GenericAPIView):
    permission_classes = [IsAuthority]
    serializer_class = CategorySerializer
    queryset = Job_Category.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            category = serializer.validated_data['category']
            category_lower = category.lower()  # Convert input category to lowercase
            # Check if category already exists (case-insensitive)
            if self.queryset.filter(category__iexact=category_lower).exists():
                response = {
                    'status': 400,
                    'message': 'Category already exists'
                }
                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
            else:
                cat = Job_Category(category=category)
                cat.save()
                response = {
                    'status': 201,
                    'message': 'New category added successfully'
                }
                return Response(data=response, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        search_param = request.data.get('search')
        cat_id = request.data.get('cat_id')
        if search_param:
            category = self.queryset.filter(category__icontains=search_param)
            if category.exists():
                serializer = self.serializer_class(category, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            response={
                'status':404,
                'message':'No data found'
            }
            return Response(data=response,status=status.HTTP_404_NOT_FOUND)
        if cat_id is not None:
            cat = get_object_or_404(Job_Category, pk=cat_id)
            serializer = self.serializer_class(instance=cat)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            if self.get_queryset().exists():
                serializer = self.serializer_class(self.get_queryset(), many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            response={
                'status':404,
                'message':'No data found'
            }
            return Response(data=response,status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        cat_id = request.data.get('cat_id')
        if cat_id:
            try:
                cat = Job_Category.objects.get(id=cat_id)
            except:
                response={
                    'status':400,
                    'message':'wrong category id'
                }
                return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
            cat.delete()
            response = {
                'status': 200,
                'message': 'Category deleted successfully'
            }
            return Response(data=response, status=status.HTTP_200_OK)

    def put(self, request):
        cat_id = request.data.get('cat_id')
        cat = get_object_or_404(Job_Category, pk=cat_id)
        data = request.data
        serializer = self.serializer_class(instance=cat, data=data)
        if serializer.is_valid():
            serializer.save()
            response = {
                'status': 200,
                'message': 'Category updated successfully',
                'data': serializer.data
            }
            return Response(data=response, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(GenericAPIView):
    permission_classes = [IsAuthority]
    serializer_class = UserSerializer
    queryset = Users.objects.filter(is_user=1, is_verified=True).select_related('user').all()

    def get(self, request):
        search_param = request.data.get('search')
        user_id = request.data.get('user_id')
        if search_param:
            users = self.queryset.filter(Q(username__icontains=search_param) | Q(email__icontains=search_param))
            if users.exists():
                serializer = self.serializer_class(users, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            response={
                'status':404,
                'message':'No data found'
            }
            return Response(data=response,status=status.HTTP_404_NOT_FOUND)
        elif user_id:
            user = get_object_or_404(self.get_queryset(), id=user_id)
            serializer = self.serializer_class(user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            if self.get_queryset().exists():
                serializer = self.serializer_class(self.get_queryset(), many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            response={
                'status':404,
                'message':'No data found'
            }
            return Response(data=response,status=status.HTTP_404_NOT_FOUND)


class BlockUser(GenericAPIView):
    permission_classes = [IsAuthority]
    serializer_class = UserSerializer
    queryset = Users.objects.filter(is_user=1).all()

    def patch(self, request):
        user_id = request.data.get('user_id')
        user = get_object_or_404(self.get_queryset(), id=user_id)
        if user.is_active is True:
            user.is_active = False
            user.save()
            serializer = self.serializer_class(user)
            response = {
                'status': 200,
                'message': 'User blocked successfully',
                'data': serializer.data
            }
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                'status': 400,
                'message': 'User is already blocked'
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


class UnblockUser(GenericAPIView):
    permission_classes = [IsAuthority]
    serializer_class = UserSerializer
    queryset = Users.objects.filter(is_user=1).all()

    def patch(self, request):
        user_id = request.data.get('user_id')
        user = get_object_or_404(self.get_queryset(), id=user_id)
        if user.is_active is False:
            user.is_active = True
            user.save()
            serializer = self.serializer_class(user)
            response = {
                'status': 200,
                'message': 'User unblocked successfully',
                'data': serializer.data
            }
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                'status': 400,
                'message': 'User is already active'
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


class WorkerView(GenericAPIView):
    permission_classes = [IsAuthority]
    serializer_class = WorkerSerializer
    # queryset = Users.objects.filter(Q(is_staff=True) & Q(is_verified=True)).select_related('worker').all()
    queryset = Users.objects.filter(Q(is_staff=True) & Q(is_verified=True)).all()
    def get(self, request):
        worker_id = request.data.get('worker_id')
        search_param = request.data.get('search')
        if search_param:
            workers = self.get_queryset().filter(Q(username__icontains=search_param) | Q(email__icontains=search_param))
            if workers.exists():
                serializer = self.serializer_class(workers, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            response={
                'status':404,
                'message':'No data found'
            }
            return Response(data=response,status=status.HTTP_404_NOT_FOUND)
        elif worker_id:
            worker = self.get_queryset().filter(id=worker_id).first()
            if worker:
                serializer = self.serializer_class(worker)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            response={
                'status':404,
                'message':'No data found'
            }
            return Response(data=response,status=status.HTTP_404_NOT_FOUND)
        else:
            if self.get_queryset().exists():
                serializer = self.serializer_class(self.get_queryset(), many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            response={
                'status':404,
                'message':'No data found'
            }
            return Response(data=response,status=status.HTTP_404_NOT_FOUND)


class BlockWorker(GenericAPIView):
    permission_classes = [IsAuthority]
    serializer_class = WorkerSerializer
    queryset = Users.objects.filter(is_staff=True).all()

    def patch(self, request):
        worker_id = request.data.get('worker_id')
        worker = get_object_or_404(self.get_queryset(), id=worker_id)
        if worker.is_active is True:
            worker.is_active = False
            worker.save()
            serializer = self.serializer_class(worker)
            response = {
                'status': 200,
                'message': 'Worker blocked successfully',
                'data': serializer.data
            }
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                'status': 400,
                'message': 'Worker is already blocked or not confirmed'
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


class UnblockWorker(GenericAPIView):
    permission_classes = [IsAuthority]
    serializer_class = WorkerSerializer
    queryset = Users.objects.filter(is_staff=True).all()

    def patch(self, request):
        worker_id = request.data.get('worker_id')
        worker = get_object_or_404(self.get_queryset(), id=worker_id)
        if worker.is_active is False:
            worker.is_active = True
            worker.save()
            serializer = self.serializer_class(worker)
            response = {
                'status': 200,
                'message': 'Worker unblocked successfully',
                'data': serializer.data
            }
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                'status': 400,
                'message': 'Worker is alredy active'
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


class Bookings(GenericAPIView):
    permission_classes = [IsAuthority]
    serializer_class = BookingSerializer

    def get(self, request):
        status = request.data.get('status')
        if status is not None:
            booking = Booking.objects.filter(status=status)
        else:
            booking = Booking.objects.all()
        if booking.exists():
            serializer = self.serializer_class(booking, many=True)
            return Response(data=serializer.data)
        else:
            response = {
                'status': 200,
                'message': 'No data found'
            }
            return Response(data=response)

    def patch(self, request):
        booking_id = request.data.get('booking_id')
        reason = request.data.get('reason')
        try:
            booking = Booking.objects.get(pk=booking_id)
        except Exception:
            response = {
                'status': 404,
                'message': 'Booking not found.'
            }
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)
        if booking.status == 'terminated':
            response = {
                'status': 400,
                'message': 'Booking is already terminated'
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        elif reason is not None and booking.status != 'completed':
            booking.status = 'terminated'
            booking.payment_status = 'cancelled'
            booking.cancellation_reason = reason
            booking.save()
            chat_room = chatroom.objects.get(name=booking.booking_id)
            if chat_room:
                chat_room.delete()
            response = {
                'status': 200,
                'message': 'Booking terminated successfully.'
            }
            return Response(data=response, status=status.HTTP_200_OK)
        elif reason is None:
            response = {
                'status': 400,
                'message': 'Please provide the reason for termination.'
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                'status': 400,
                'message': 'The booking status is completed so you cant terminate it.'
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


class AuthorityPrivacy(GenericAPIView):
    permission_classes = [IsAuthority]
    serializer_class = PrivacySerializer

    def patch(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data)
        if serializer.is_valid():
            # Check if the current password provided matches the user's actual password
            current_password = serializer.validated_data.get('password')
            if check_password(current_password, user.password):
                new_password = serializer.validated_data.get('new_password')
                confirm_password = serializer.validated_data.get('confirm_password')
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    response = {
                        'status': 200,
                        'message': 'Your Password Updated successfully'
                    }
                    return Response(data=response, status=status.HTTP_200_OK)
                else:
                    response = {
                        'status': 400,
                        'message': 'New password and confirm password are not matching'
                    }
                    return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
            else:
                response = {
                    'status': 400,
                    'message': 'You have provided the wrong password'
                }
                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
