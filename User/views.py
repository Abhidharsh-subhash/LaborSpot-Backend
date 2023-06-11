from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from.serializers import SignUpSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

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
                'data':serializer.data
            }
            return Response(data=response,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request:Request):
        content={
            'message':'It is for User signup only POST request is allowed'
        }
        return Response(data=content,status=status.HTTP_200_OK)
