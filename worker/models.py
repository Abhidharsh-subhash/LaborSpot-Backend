from django.db import models
from Authority.models import Users

# Create your models here.

class Worker_detials(models.Model):
    user=models.OneToOneField(Users,on_delete=models.CASCADE,related_name='user')
    category=models.ForeignKey()
    experience=models.IntegerField()
    charge=models.IntegerField()
    phone_number=models.IntegerField()
    photo=models.ImageField('image',upload_to='userimages/')