from rest_framework import serializers
from .models import Worker_details
from Authority.models import Users,Job_Category
from django.core.validators import EmailValidator
from rest_framework.validators import ValidationError
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed
# from .send_sms import forgot_sms

class PhoneValidator(RegexValidator):
    regex = r'^\+?[1-9]\d{9}$'
    message = "Enter a valid phone number."

class OTPValidator(RegexValidator):
    regex = r'^\d{4}$'
    message = "Enter a valid OTP with 4 digits."

class UsernameValidator(RegexValidator):
    regex = r'^[a-zA-Z]+$'
    message = "Enter a valid username with only characters."

class ExperienceValidator(RegexValidator):
    regex = r'^\d{1,2}$'
    message = "Enter a valid experience."

class WorkerDetialsSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[PhoneValidator()])
    experience = serializers.IntegerField(validators=[ExperienceValidator()])
    charge = serializers.IntegerField()
    category=serializers.PrimaryKeyRelatedField(queryset=Job_Category.objects.all())
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        if Worker_details.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('Phone number already exists')
        return super().validate(attrs)

    class Meta:
        model = Worker_details
        fields = ['category','experience','charge','phone_number','photo']

class SignupSerializer(serializers.ModelSerializer):
    Worker_details = WorkerDetialsSerializer()
    email=serializers.CharField(validators=[EmailValidator()])
    username=serializers.CharField(validators=[UsernameValidator()])
    password=serializers.CharField()
    class Meta:
        model = Users
        fields = ['email', 'username', 'password', 'Worker_details']
    def validate(self, attrs):
        queryset = Users.objects.filter(is_staff=True)
        email_exists = queryset.filter(email=attrs['email']).exists()
        if email_exists:
            raise ValidationError('Email has already been used')
        else:
            return super().validate(attrs)
    def create(self, validated_data):
        password=validated_data.pop('password')
        Worker_details_data=validated_data.pop('Worker_details')
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

class VerifyAccountSerializer(serializers.Serializer):
    phone_number=serializers.CharField(validators=[PhoneValidator()])
    otp=serializers.CharField(validators=[OTPValidator()])

class WorkerLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(validators=[EmailValidator()])
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
    
class ForgotPasswordSerializer(serializers.ModelSerializer):
    phone_number=serializers.CharField(validators=[PhoneValidator])
    class Meta:
        model=Worker_details
        fields=['phone_number']
    def validate(self, attrs):
        phone_number=attrs.get('phone_number')
        try:
            worker=Worker_details.objects.get(phone_number=phone_number)
            user = worker.worker
            mail=user.email
            # forgot_sms(phone_number,mail)
        except Worker_details.DoesNotExist:
            raise AuthenticationFailed('Worker with the provided phone number doest not exist')
        return user

class VerifyForgot(serializers.ModelSerializer):
    pass

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Job_Category
        fields=['category']

class WorkerDerialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker_details
        fields = ['experience','charge','photo']

class WorkerProfileSerializer(serializers.ModelSerializer):
    worker_details=WorkerDerialSerializer(required=True,source='worker')
    category = JobCategorySerializer(source='worker.category')
    # experience=serializers.SerializerMethodField()
    # charge=serializers.SerializerMethodField()
    # phone_number=serializers.SerializerMethodField()
    def get_experience(self,obj):
        try:
            # exp_detail=Worker_details.objects.get(worker=obj.id)
            exp_detail=obj.worker.experience
            return exp_detail
        except Worker_details.DoesNotExist:
            return None
    def get_charge(self,obj):
        try:
            # cha_detail=Worker_details.objects.get(worker=obj.id)
            cha_detail=obj.worker.charge
            return cha_detail
        except Worker_details.DoesNotExist:
            return None
    def get_phone_number(self,obj):
        try:
            # ph_detail=Worker_details.objects.get(worker=obj.id)
            ph_detail=obj.worker.phone_number
            return ph_detail
        except Worker_details.DoesNotExist:
            return None
    class Meta:
        model=Users
        fields=['username','email','category','worker_details']
