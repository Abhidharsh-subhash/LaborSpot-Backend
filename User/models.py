from django.db import models
from Authority.models import Users

# Create your models here.

class User_detials(models.Model):
    user=models.ForeignKey(Users,on_delete=models.CASCADE,related_name='extra_userdetials')
    phone_number=models.IntegerField()
    photo=models.ImageField('image',upload_to='userimages/')
