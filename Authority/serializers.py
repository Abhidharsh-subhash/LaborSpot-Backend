from rest_framework import serializers
from .models import Users,Job_Category,Booking
from User.models import User_details
from Worker.models import Worker_details
from django.core.validators import EmailValidator
from django.core.validators import RegexValidator

class CategoryValidator(RegexValidator):
    regex = r'^[a-zA-Z]+$'
    message = "Enter a valid username with only characters."

class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(validators=[EmailValidator()])
    password=serializers.CharField()
    class Meta:
        model = Users
        fields = ['email','password']

class UserSerializer(serializers.ModelSerializer):
    phone_number=serializers.SerializerMethodField()
    def get_phone_number(self,obj):
        try:
            detail=User_details.objects.get(user=obj.id)
            return detail.phone_number
        except User_details.DoesNotExist:
            return None
    class Meta:
        model = Users
        fields = ['id','username','email','is_active','phone_number']

class CategorySerializer(serializers.ModelSerializer):
    category=serializers.CharField(max_length=30,validators=[CategoryValidator()])
    class Meta:
        model = Job_Category
        fields = '__all__'

class JobcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Category
        fields = ['category'] 

class WorkerSerializer(serializers.ModelSerializer):
    category = JobcategorySerializer(source='worker.category')
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
        fields=['id','username','email','is_active','category','experience','charge','phone_number']

class Bookingserializer(serializers.ModelSerializer):
    username=serializers.SerializerMethodField()
    workername=serializers.SerializerMethodField()
    def get_username(self,obj):
        try:
            user=Users.objects.get(pk=obj.user.id)
            return user.username
        except Exception:
            return None
    def get_workername(self,obj):
        try:
            worker=Users.objects.get(pk=obj.user.id)
            return worker.username
        except Exception:
            return None
    class Meta:
        model = Booking
        fields = ['id','username','workername','date','time_from','time_to','payment_amount','payment_status','location','contact_information','instructions','status','cancellation_reason']

class PrivacySerializer(serializers.ModelSerializer):
    password=serializers.CharField(style={'input-type':'password'})
    new_password=serializers.CharField(style={'input-type':'password'})
    confirm_password=serializers.CharField(style={'input-type':'password'})
    class Meta:
        model = Users
        fields = ['password','new_password','confirm_password']