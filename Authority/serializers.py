from rest_framework import serializers
from .models import Users,Job_Category
from User.models import User_detials
from Worker.models import Worker_detials

class UserSerializer(serializers.ModelSerializer):
    phone_number=serializers.SerializerMethodField()
    def get_phone_number(self,obj):
        try:
            detail=User_detials.objects.get(user=obj.id)
            return detail.phone_number
        except User_detials.DoesNotExist:
            return None
    class Meta:
        model = Users
        fields = ['id','username','email','is_active','phone_number']

class CategorySerializer(serializers.ModelSerializer):
    category=serializers.CharField(max_length=30)
    class Meta:
        model = Job_Category
        fields = '__all__'

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Category
        fields = ['category'] 

class WorkerSerializer(serializers.ModelSerializer):
    category = JobCategorySerializer(source='worker.category')
    # category=serializers.SerializerMethodField()
    experience=serializers.SerializerMethodField()
    charge=serializers.SerializerMethodField()
    phone_number=serializers.SerializerMethodField()
    # def get_category(self,obj):
    #     try:
    #         cat_detail=Worker_detials.objects.get(worker=obj.id)
    #         return cat_detail.category
    #     except Worker_detials.DoesNotExist:
    #         return None
    def get_experience(self,obj):
        try:
            exp_detail=Worker_detials.objects.get(worker=obj.id)
            return exp_detail.experience
        except Worker_detials.DoesNotExist:
            return None
    def get_charge(self,obj):
        try:
            cha_detail=Worker_detials.objects.get(worker=obj.id)
            return cha_detail.charge
        except Worker_detials.DoesNotExist:
            return None
    def get_phone_number(self,obj):
        try:
            ph_detail=Worker_detials.objects.get(worker=obj.id)
            return ph_detail.phone_number
        except User_detials.DoesNotExist:
            return None
    class Meta:
        model=Users
        fields=['id','username','email','is_active','category','experience','charge','phone_number']