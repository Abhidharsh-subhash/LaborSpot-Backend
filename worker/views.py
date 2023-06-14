from django.shortcuts import render
from.serializers import SignupSerializer,WorkerLoginSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

class WorkerSignUpView(GenericAPIView):
    serializer_class=SignupSerializer
    def post(self,request:Request):
        data=request.data
        serializer=self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            response={
                'message':'Worker created successfully',
            }
            return Response(data=response,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request:Request):
        content={
            'message':'It is for Worker signup only POST request is allowed'
        }
        return Response(data=content,status=status.HTTP_200_OK)
    
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
