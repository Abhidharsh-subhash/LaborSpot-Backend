from rest_framework import serializers
from .models import Worker_details
from Authority.models import Users,Job_Category
from django.core.validators import EmailValidator
from rest_framework.validators import ValidationError
from django.contrib.auth import authenticate
from django.db import transaction

class WorkerDetialsSerializer(serializers.ModelSerializer):
    category=serializers.PrimaryKeyRelatedField(queryset=Job_Category.objects.all())
    class Meta:
        model = Worker_details
        fields = ['category','experience','charge','phone_number','photo']

class SignupSerializer(serializers.ModelSerializer):
    Worker_details = WorkerDetialsSerializer()
    email=serializers.CharField(validators=[EmailValidator()])
    class Meta:
        model = Users
        fields = ['email', 'username', 'password', 'Worker_detials']
    def validate(self, attrs):
        queryset = Users.objects.filter(is_staff=True)
        email_exists = queryset.filter(email=attrs['email']).exists()
        if email_exists:
            raise ValidationError('Email has already been used')
        else:
            return super().validate(attrs)
    def create(self, validated_data):
        password=validated_data.pop('password')
        Worker_details_data=validated_data.pop('Worker_detials')
        validated_data['is_staff']=True
        with transaction.atomic():
            try:
                user=super(SignupSerializer,self).create(validated_data)
                user.set_password(password)
                user.save()
                Worker_details.objects.create(worker=user,**Worker_details_data)
            except Exception as e:
                user.delete()
                raise e
        return user

class WorkerLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField()
    password=serializers.CharField(style={'input-type':'password'})
    class Meta:
        model = Users
        fields = ['email','password']
    def validate(self, attrs):
        email=attrs.get('email')
        password=attrs.get('password')
        if email and password:
            user=authenticate(email=email,password=password)
            if user:
                if not (user.is_staff and  user.is_verified):
                    raise serializers.ValidationError('You are not authorized to perform this action')
                else:
                    attrs['user']=user
            else:
                raise serializers.ValidationError('Invalid Username or Password')
        else:
            raise serializers.ValidationError('Username and Password are required')
        return attrs