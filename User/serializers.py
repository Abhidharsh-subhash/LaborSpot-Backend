from Authority.models import Users
from rest_framework.validators import ValidationError
from rest_framework import serializers
from .models import User_detials

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_detials
        fields = ['phone_number', 'photo']

class SignUpSerializer(serializers.ModelSerializer):
    email=serializers.CharField(max_length=80)
    username=serializers.CharField(max_length=45)
    #write_only is used to keep our password private
    password=serializers.CharField(min_length=8,write_only=True)
    phone_number = serializers.IntegerField()
    photo = serializers.ImageField()
    user_details = UserDetailsSerializer()  # Nested serializer
    class Meta:
        model=Users
        # fields = '__all__'  # if you need to specify all the fields in the model
        fields=['email','username','password','photo', 'phone_number', 'user_details']
    def validate(self, attrs):
        email_exists=Users.objects.filter(email=attrs['email']).exists()
        if email_exists:
            raise ValidationError('Email has already been used')
        else:
            return super().validate(attrs)
    #custom create method to hash the passwords of the users
    def create(self, validated_data):
        password=validated_data.pop('password')
        phone_number = validated_data.pop('phone_number')
        photo = validated_data.pop('photo')
        user_details_data = validated_data.pop('user_details')
        validated_data['is_user'] = 1 
        user=super().create(validated_data)
        user.set_password(password)
        user.save()
        User_detials.objects.create(user=user,phone_number=phone_number, photo=photo,**user_details_data)
        return user