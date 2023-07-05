from datetime import date,datetime
from Authority.models import Users
from rest_framework.validators import ValidationError
from rest_framework import serializers
from .models import User_details
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.core.validators import EmailValidator
from django.db import transaction
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from rest_framework.exceptions import AuthenticationFailed
from Authority.models import Job_Category,Booking
from Worker.models import Worker_details

class PhoneValidator(RegexValidator):
    regex = r'^\+?[1-9]\d{9}$'
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
    
class ForgotPasswordSerializer(serializers.ModelSerializer):
    email = serializers.CharField(validators=[EmailValidator()])
    class Meta:
        model = Users
        fields = ['email']

class SetNewPasswordSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)
    token=serializers.CharField(write_only=True)
    uidb64=serializers.CharField(write_only=True)
    class Meta:
        model=Users
        fields=['password','token','uidb64']
    def validate(self, attrs):
        try:
            password=attrs.get('password')
            token=attrs.get('token')
            uibd64=attrs.get('uidb64')
            id=force_str(urlsafe_base64_decode(uibd64))
            user=Users.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise AuthenticationFailed('The reset link is invalid',401)
            user.set_password(password)
            user.save()
            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid',401)

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Category
        fields = ['category']

class WorkerListSerializer(serializers.ModelSerializer):
    category = JobCategorySerializer(source='worker.category')
    experience=serializers.SerializerMethodField()
    charge=serializers.SerializerMethodField()
    phone_number=serializers.SerializerMethodField()

    def get_experience(self,obj):
        try:
            exp_detail=Worker_details.objects.get(worker=obj.id)
            return exp_detail.experience
        except Worker_details.DoesNotExist:
            return None
    def get_charge(self,obj):
        try:
            cha_detail=Worker_details.objects.get(worker=obj.id)
            return cha_detail.charge
        except Worker_details.DoesNotExist:
            return None
    def get_phone_number(self,obj):
        try:
            ph_detail=Worker_details.objects.get(worker=obj.id)
            return ph_detail.phone_number
        except Worker_details.DoesNotExist:
            return None
    class Meta:
        model=Users
        fields=['id','username','email','category','experience','charge','phone_number']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_details
        fields = ['phone_number', 'photo']

class UserProfileSerializer(serializers.ModelSerializer):
    user_details = UserDetailSerializer(required=False)
    phone_number = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    def get_phone_number(self,obj):
        try:
            # detail=User_details.objects.get(user=obj.id)
            detail = obj.user.phone_number
            return detail
        except User_details.DoesNotExist:
            return None
    def get_photo(self,obj):
        try:
            # detail=User_details.objects.get(user=obj.id)
            detail = obj.user.photo.url
            return detail
        except User_details.DoesNotExist:
            return None
    class Meta:
        model = Users
        fields = ['username','email','phone_number','photo','user_details']

class UserPrivacySerializer(serializers.ModelSerializer):
    password=serializers.CharField(style={'input-type':'password'})
    new_password=serializers.CharField(style={'input-type':'password'})
    confirm_password=serializers.CharField(style={'input-type':'password'})
    def validate(self, attrs):
        new_password=attrs.get('new_password')
        confirm_password=attrs.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError('The new password and confirm passowrd are not matching')
        return attrs
    class Meta:
        model = Users
        fields = ['password','new_password','confirm_password']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['user','worker', 'date', 'time_from', 'time_to','location', 'contact_information', 'instructions','payment_amount']

    def validate(self, data):
        # Validate the 'date' field
        if 'date' in data:
            today = date.today()
            value = data['date']
            value = value.strftime('%Y-%m-%d')  # Convert date object to string
            value = datetime.strptime(value, '%Y-%m-%d').date()  # Convert string to date object
            if value <= today:
                raise serializers.ValidationError("Date must be from tomorrow onwards.")
            data['date'] = value
        # Validate the time range
        if 'time_from' in data and 'time_to' in data:
            time_from = data['time_from']
            time_to = data['time_to']
            if time_from >= time_to:
                raise serializers.ValidationError("Invalid time range. 'time_from' should be before 'time_to'.")
        return data