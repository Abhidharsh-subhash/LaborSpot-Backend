from Authority.models import Users
from rest_framework.validators import ValidationError
from rest_framework import serializers
from .models import User_detials
from django.contrib.auth import authenticate

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_detials
        fields = ['phone_number', 'photo']

class SignUpSerializer(serializers.ModelSerializer):
    user_details = UserDetailsSerializer()
    class Meta:
        model = Users
        fields = ['email', 'username', 'password', 'user_details']
        # fields = '__all__'
    
    def validate(self, attrs):
        email_exists = Users.objects.filter(email=attrs['email']).exists()
        if email_exists:
            raise ValidationError('Email has already been used')
        else:
            return super().validate(attrs)
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user_detials_data = validated_data.pop('user_details')
        validated_data['is_user'] = 1
        user = super(SignUpSerializer, self).create(validated_data)
        user.set_password(password)
        user.save()
        User_detials.objects.create(user=user, **user_detials_data)
        return user
    


# class SignUpSerializer(serializers.ModelSerializer):
#     user=serializers.SerializerMethodField()
#     def get_user(self,user):
#         user,created=Users.objects.get_or_create(email=user.email,username=user.username,is_user=1)
#         if created:
#             user=Users.objects.get(email=user.email)
#             user.set_password(user.password)
#             user.save()
#     class Meta:
#         model=User_detials
#         fields=['user','phone_number','photo']
# class SignUpSerializer(serializers.ModelSerializer):
#     user_details = UserDetailsSerializer()
#     class Meta:
#         model=Users
#         # fields = '__all__'  # if you need to specify all the fields in the model
#         fields=['email','username','password','user_details']
#     def validate(self, attrs):
#         email_exists=Users.objects.filter(email=attrs['email']).exists()
#         if email_exists:
#             raise ValidationError('Email has already been used')
#         else:
#             return super().validate(attrs)
#     #custom create method to hash the passwords of the users
#     def create(self, validated_data):
#         password=validated_data.pop('password')
#         user_details_data = validated_data.pop('user_details')
#         validated_data['is_user'] = 1 
#         # user=super().create(validated_data)
#         user = Users.objects.create(**validated_data)
#         user.set_password(password)
#         user.save()
#         User_detials.objects.create(user=user,**user_details_data)
#         return user  
    
class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField()
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
                if not (user.is_user == 1):
                    raise serializers.ValidationError('You are not authorized to perform this action')
                else:
                    attrs['user']=user
            else:
                raise serializers.ValidationError('Invalid username or password')
        else:
            raise serializers.ValidationError('Email and Password are required')
        return attrs