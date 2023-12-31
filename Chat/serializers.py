from rest_framework import serializers
from .models import *
from Authority.models import Users
from Authority.serializers import UserSerializer

from rest_framework import serializers
from .models import ChatMessage

class ChatSerializer(serializers.ModelSerializer):
    sender = UserSerializer()

    class Meta:
        model = ChatMessage
        fields = ('sender', 'message' ,'time')
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()

    # def get_sender(self, message):
    #     return {
    #         'id': message.sender.id,
    #         'username': message.sender.username
    #         # Include other desired fields from the UserAccount model
    #     }

    class Meta:
        model = ChatMessage
        fields = ('room', 'sender', 'message', 'time')