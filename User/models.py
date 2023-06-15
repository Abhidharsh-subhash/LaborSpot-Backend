from django.db import models
from Authority.models import Users

# Create your models here.

class User_details(models.Model):
    user=models.OneToOneField(Users,on_delete=models.CASCADE,related_name='user')
    phone_number=models.IntegerField()
    photo=models.ImageField('image',upload_to='userimages/')

    def __str__(self) -> str:
        return self.user.username
