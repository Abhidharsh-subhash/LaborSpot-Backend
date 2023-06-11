from rest_framework.request import Request
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

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
