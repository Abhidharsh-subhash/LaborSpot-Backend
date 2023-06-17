from Authority.models import Users
from rest_framework.validators import ValidationError
from rest_framework import serializers
from .models import User_details
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.core.validators import EmailValidator
from django.db import transaction

class PhoneValidator(RegexValidator):
    regex = r'^\+?[1-9]\d{1,14}$'
    message = "Enter a valid phone number."

class OTPValidator(RegexValidator):
    regex = r'^\d{4}$'
    message = "Enter a valid OTP with 4 digits."

class UserDetailsSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[PhoneValidator()])
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        if User_details.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('Phone number already exists')
        return super().validate(attrs)
    class Meta:
        model = User_details
        fields = ['phone_number', 'photo']

class SignUpSerializer(serializers.ModelSerializer):
    user_details = UserDetailsSerializer()
    email = serializers.CharField(validators=[EmailValidator()])
    class Meta:
        model = Users
        fields = ['email', 'username', 'password', 'user_details']
        # fields = '__all__'
    
    def validate(self, attrs):
        queryset = Users.objects.filter(is_user=1).all()
        email_exists = queryset.filter(email=attrs['email']).exists()
        if email_exists:
            raise ValidationError('Email has already been used')
        else:
            return super().validate(attrs)
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user_details_data = validated_data.pop('user_details')
        validated_data['is_user'] = 1
        with transaction.atomic():
            try:
                user = super(SignUpSerializer, self).create(validated_data)
                user.set_password(password)
                user.save()
                User_details.objects.create(user=user, **user_details_data)
            except Exception as e:
                user.delete()
                raise e
        return user

class VerifyAccountSerializer(serializers.Serializer):
    email=serializers.EmailField(validators=[EmailValidator()])
    otp=serializers.CharField(validators=[OTPValidator()])
    
class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(validators=[EmailValidator()])
    password=serializers.CharField(style={'input-type':'password'})
    class Meta:
        model=Users
        fields=['email','password']
    def validate(self, attrs):
        email=attrs.get('email')
        password=attrs.get('password')
        if email and password:
            user=authenticate(email=email,password=password)
            if user:
                if not (user.is_user == 1 and user.is_verified):
                    raise serializers.ValidationError('You are not authorized to perform this action')
                else:
                    attrs['user']=user
            else:
                raise serializers.ValidationError('Invalid username or password')
        else:
            raise serializers.ValidationError('Email and Password are required')
        return attrs