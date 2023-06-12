from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from.serializers import SignUpSerializer,UserLoginSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

class UserSignUpView(GenericAPIView):
    serializer_class=SignUpSerializer
    def post(self,request:Request):
        data=request.data
        serializer=self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            response={
                'message':'User created successfully',
            }
            return Response(data=response,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request:Request):
        content={
            'message':'It is for User signup only POST request is allowed'
        }
        return Response(data=content,status=status.HTTP_200_OK)
    
class UserLoginView(APIView):
    serializer_class=UserLoginSerializer
    def post(self,request:Request):
        data=request.data
        serializer=self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        tokens=RefreshToken.for_user(user)
        response={
                'message':'User login successful',
                'access':str(tokens.access_token),
                'refresh':str(tokens)
            }
        return Response(data=response,status=status.HTTP_200_OK)  
    def get(self,request):
        content={
            'message':'It is for User login only POST request is allowed'
        }
        return Response(data=content,status=status.HTTP_200_OK)
