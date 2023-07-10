import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import chatroom,ChatMessage
from Authority.models import Users
from .serializers import *


class ChatConsumer(AsyncWebsocketConsumer):
    print("HELLO")

    async def connect(self):
        print("HELLO")
        room_id = self.scope['url_route']['kwargs']['room_id']
        # try:
        #     room_id = chatroom.objects.get(name=id)
        #     room_id=room_id.id

        # except chatroom.DoesNotExist:
        #     await self.close()
        print(room_id)
        self.room_group_name = f'chat_{room_id}'

        exists = await sync_to_async(chatroom.objects.filter(name=room_id).exists)()

        if exists:
            self.room_name = room_id
            self.scope['room_id'] = room_id

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            # Handle the case when the room with the provided ID does not exist
            await self.close()

    async def disconnect(self, close_code):
        print(close_code)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("RECEIVE")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']
        receiver_id = text_data_json['receiver_id']

        room = await sync_to_async(chatroom.objects.get)(name=self.room_name)
        sender = await sync_to_async(Users.objects.get)(id=sender_id)
        receiver = await sync_to_async(Users.objects.get)(id=receiver_id)
        print("room",self.room_name)

        chat_message = await sync_to_async(ChatMessage.objects.create)(
            room=room,
            sender=sender,
            receiver=receiver,
            message=message
        )

        serializer = MessageSerializer(chat_message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': serializer.data
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))