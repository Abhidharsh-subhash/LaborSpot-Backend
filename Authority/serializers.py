from rest_framework import serializers
from .models import Users,Job_Category
from User.models import User_detials

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
