from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser

# Create your models here.

#created custom boolean field where 0 is false and 1 is true
# class CustomBooleanField(models.BooleanField):
#     def to_python(self, value):
#         if value in (0, 1):
#             return bool(value)
#         return super().to_python(value)

class CustomUserManager(BaseUserManager):
    def create_user(self,email,password,**extra_fields):
        email=self.normalize_email(email)
        user=self.model(
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_verified',True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser has to have is_superuser being True')
        return self.create_user(email=email,password=password,**extra_fields)

class Users(AbstractUser):
    choices = {
        (0, 'False'),
        (1, 'True'),
    }
    email=models.CharField(max_length=80,unique=True)
    username=models.CharField(max_length=45)
    is_user=models.IntegerField(choices=choices,default=0)
    is_verified=models.BooleanField(default=False)
    otp=models.CharField(max_length=6,null=True,blank=True)

    objects=CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
    
class Job_Category(models.Model):
    category=models.CharField(max_length=30)

    def __str__(self):
        return self.category

class Booking(models.Model):
    booking_id=models.CharField(max_length=10,null=False)
    user = models.ForeignKey(Users,on_delete=models.CASCADE,related_name='booked_user')
    worker = models.ForeignKey(Users,on_delete=models.CASCADE,related_name='worker_booked')
    date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    payment_amount = models.IntegerField()
    payment_status = models.CharField(max_length=30,default='pending')
    location = models.CharField(max_length=30)
    contact_information = models.CharField(max_length=100)
    instructions = models.CharField(max_length=100)
    status = models.CharField(max_length=20,default='pending')
    cancellation_reason = models.CharField(max_length=100,null=True)
    feedback = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.id} - Order Status: {self.status}, Payment Status: {self.payment_status}"