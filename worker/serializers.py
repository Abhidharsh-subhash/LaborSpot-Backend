from rest_framework import serializers
from .models import Worker_detials
from Authority.models import Users,Job_Category
from django.core.validators import EmailValidator
from rest_framework.validators import ValidationError

class WorkerDetialsSerializer(serializers.ModelSerializer):
    category=serializers.PrimaryKeyRelatedField(queryset=Job_Category.objects.all())
    class Meta:
        model = Worker_detials
        fields = ['category','experience','charge','phone_number','photo']

class SignupSerializer(serializers.ModelSerializer):
    Worker_detials = WorkerDetialsSerializer()
    email=serializers.CharField(validators=[EmailValidator()])
    class Meta:
        model = Users
        fields = ['email', 'username', 'password', 'Worker_detials']
    def validate(self, attrs):
        email_exists = Users.objects.filter(email=attrs['email']).exists()
        if email_exists:
            raise ValidationError('Email has already been used')
        else:
            return super().validate(attrs)
    def create(self, validated_data):
        password=validated_data.pop('password')
        Worker_detials_data=validated_data.pop('Worker_detials')
        validated_data['is_staff']=True
        user=super(SignupSerializer,self).create(validated_data)
        user.set_password(password)
        user.save()
        Worker_detials.objects.create(user=user,**Worker_detials_data)
        return user