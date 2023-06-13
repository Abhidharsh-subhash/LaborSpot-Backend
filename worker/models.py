from django.db import models
from Authority.models import Users,Job_Category

# Create your models here.

class Worker_detials(models.Model):
    user=models.OneToOneField(Users,on_delete=models.CASCADE,related_name='worker')
    category=models.ForeignKey(Job_Category,on_delete=models.CASCADE,related_name='cat')
    experience=models.IntegerField()
    charge=models.IntegerField()
    phone_number=models.IntegerField()
    photo=models.ImageField('image',upload_to='userimages/')

    def __str__(self):
        return self.user.username