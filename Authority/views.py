from rest_framework.request import Request
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer,CategorySerializer,WorkerSerializer
from .models import Users,Job_Category
from User.models import User_detials
from django.shortcuts import get_object_or_404
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser,IsAuthenticated

# Create your views here.

class AuthorityLoginApiview(APIView):
    def post(self,request:Request):
        email=request.data.get('email')
        password=request.data.get('password')
        user=authenticate(email=email,password=password)
        if user is None:
            return Response(data={'message':'Invalid email or password'},status=status.HTTP_401_UNAUTHORIZED)
        elif not user.is_superuser:
             return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            tokens = RefreshToken.for_user(user)
            response={
                'message':'Authority Login successfull',
                'access':str(tokens.access_token),
                'refresh':str(tokens)
            }
            return Response(data=response,status=status.HTTP_200_OK)
    def get(self,request:Request):
        print('get')
        content={
            'message':'It is for Authority login only POST request is allowed'
        }
        return Response(data=content,status=status.HTTP_200_OK)
    
class CategoryView(GenericAPIView):
    # permission_classes=[IsAdminUser]
    serializer_class=CategorySerializer
    queryset=Job_Category.objects.all()
    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            category=serializer.validated_data['category']
            cat=Job_Category(category=category)
            cat.save()
            response={
                'message':'New category added successfully'
            }
            return Response(data=response,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request,cat_id=None):
        search_param=request.query_params.get('search','')
        if search_param:
            category=self.queryset.filter(category__icontains=search_param)
            serializer=self.serializer_class(category,many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        if cat_id is not None:
            cat=get_object_or_404(Job_Category,pk=cat_id)
            serializer=self.serializer_class(instance=cat)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        else:
            serializer=self.serializer_class(self.get_queryset(),many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
    def delete(self,request,cat_id:int):
        cat=get_object_or_404(Job_Category,pk=cat_id)
        cat.delete()
        return Response(data={'message':'Category deleted successfully'},status=status.HTTP_204_NO_CONTENT)
    def put(self,request,cat_id:int):
        cat=get_object_or_404(Job_Category,pk=cat_id)
        data=request.data
        serializer=self.serializer_class(instance=cat,data=data)
        if serializer.is_valid():
            serializer.save()
            response={
                'message':'Category updated',
                'data':serializer.data
            }
            return Response(data=response,status=status.HTTP_200_OK)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
class UserView(GenericAPIView):
    # permission_classes=[IsAdminUser]
    serializer_class=UserSerializer
    queryset=Users.objects.filter(is_user=1).select_related('user').all()
    def get(self,request,user_id=None):
        search_param=request.query_params.get('search','')
        # is_blocked=request.query_params.get('blocked','')
        if search_param:
            users=self.queryset.filter(username__icontains=search_param)
            serializer=self.serializer_class(users,many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        # elif is_blocked:
        #     breakpoint()
        #     if is_blocked.lower() == 'true':
        #         users=self.queryset.filter(is_active=False)
        #         serializer=self.serializer_class(users,many=True)
        #         return Response(data=serializer.data,status=status.HTTP_200_OK)
        #     elif is_blocked.lower() == 'false':
        #         users=self.queryset.filter(is_active=False)
        #         serializer=self.serializer_class(users,many=True)
        #         return Response(data=serializer.data,status=status.HTTP_200_OK)
        #     else:
        #         response={
        #             'message':'Invalid parameter for is_blocked parameter',
        #         }
        #         return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        if user_id is None:
            serializer=self.serializer_class(self.get_queryset(),many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        else:
            user=get_object_or_404(self.get_queryset(),id=user_id)
            serializer=self.serializer_class(user)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        
class BlockUser(GenericAPIView):
    serializer_class=UserSerializer
    queryset=Users.objects.filter(is_user=1).all()
    def patch(self,request,user_id:int):
        user=get_object_or_404(self.get_queryset(),id=user_id)
        if user.is_active is True:
            user.is_active=False
            user.save()
            serializer=self.serializer_class(user)
            response={
                'message':'User blocked successfully',
                'data':serializer.data
            }
            return Response(data=response,status=status.HTTP_200_OK)
        else:
            response={
                'message':'User is already blocked'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        
class UnblockUser(GenericAPIView):
    serializer_class=UserSerializer
    queryset=Users.objects.filter(is_user=1).all()
    def patch(self,request,user_id:int):
        user=get_object_or_404(self.get_queryset(),id=user_id)
        if user.is_active is False:
            user.is_active=True
            user.save()
            serializer=self.serializer_class(user)
            response={
                'message':'User unblocked successfully',
                'data':serializer.data
            }
            return Response(data=response,status=status.HTTP_200_OK)
        else:
            response={
                'message':'User is already active'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        
class WorkerView(GenericAPIView):
    serializer_class=WorkerSerializer
    queryset=Users.objects.filter(is_staff=True).select_related('worker').all()
    def get(self,request,worker_id=None):
        search_param=request.query_params.get('search','')
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
        
class BlockWorker(GenericAPIView):
    serializer_class=WorkerSerializer
    queryset=Users.objects.filter(is_staff=True).all()
    def patch(self,request,worker_id:int):
        worker=get_object_or_404(self.get_queryset(),id=worker_id)
        if worker.is_active is True:
            worker.is_active=False
            worker.save()
            serializer=self.serializer_class(worker)
            response={
                'message':'Worker blocked successfully',
                'data':serializer.data
            }
            return Response(data=response,status=status.HTTP_200_OK)
        else:
            response={
                'message':'Worker is already blocked'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)
        
class UnblockWorker(GenericAPIView):
    serializer_class=WorkerSerializer
    queryset=Users.objects.filter(is_staff=True).all()
    def patch(self,request,worker_id:int):
        worker=get_object_or_404(self.get_queryset(),id=worker_id)
        if worker.is_active is False:
            worker.is_active=True
            worker.save()
            serializer=self.serializer_class(worker)
            response={
                'message':'Worker unblocked successfully',
                'data':serializer.data
            }
            return Response(data=response,status=status.HTTP_200_OK)
        else:
            response={
                'message':'Worker is alredy active'
            }
            return Response(data=response,status=status.HTTP_400_BAD_REQUEST)




    
