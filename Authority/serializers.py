from rest_framework import serializers
from .models import Users,Job_Category

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        models=Users
        fields='__all__'

class CategorySerializer(serializers.ModelSerializer):
    category=serializers.CharField(max_length=30)
    class Meta:
        models=Job_Category
        fields='__all__'
