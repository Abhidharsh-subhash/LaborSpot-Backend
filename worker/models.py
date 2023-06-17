from django.db import models
from Authority.models import Users,Job_Category

# Create your models here.

class Worker_details(models.Model):
    worker=models.OneToOneField(Users,on_delete=models.CASCADE,related_name='worker')
    category=models.ForeignKey(Job_Category,on_delete=models.CASCADE,related_name='cat')
    experience=models.IntegerField()
    charge=models.IntegerField()
    phone_number=models.CharField(max_length=10)
    photo=models.ImageField('image',upload_to='workerimages/')

    def __str__(self):
        return self.phone_number
