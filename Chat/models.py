from django.db import models
from Authority.models import Users

# Create your models here.
class chatroom(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(Users,related_name='chat_room')
    def __str__(self):
        return self.name
    
class ChatMessage(models.Model):
    room=models.ForeignKey(chatroom,on_delete=models.CASCADE,related_name='messages')
    sender=models.ForeignKey(Users,on_delete=models.CASCADE,related_name='sent_messages')
    message=models.TextField()
    time=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.sender.username}:{self.message}'