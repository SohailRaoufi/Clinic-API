import json
from typing import Any

from user.token_factory import decode_token
from .models import Messages, Room
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .serializers import MsgSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.files.base import ContentFile
import base64


@sync_to_async
def get_msgs(room: Room):
    messages = Messages.objects.filter(room=room)  # type:ignore
    serializer = MsgSerializer(messages, many=True)
    return serializer.data


@sync_to_async
def create_msg(room: Room, sender: User, receiver: User, msg: str):
    msg = Messages.objects.create(  # type:ignore
        sender=sender,
        room=room,
        receiver=receiver,
        type="text",
        text=msg
    )
    serializer = MsgSerializer(msg)
    return serializer.data


@sync_to_async
def create_document(room: Room, sender: User, receiver: User, document: Any, file_name: str):
    file_bytes = base64.b64decode(document)
    file = ContentFile(file_bytes, name=file_name)
    msg = Messages.objects.create(  # type:ignore
        sender=sender,
        room=room,
        receiver=receiver,
        type="link",
        link=file
    )
    serializer = MsgSerializer(msg)
    return serializer.data


@sync_to_async
def get_user(email: str):
    try:
        user = User.objects.get(email=email)
        return user, True
    except User.DoesNotExist:  # type:ignore
        return None, False

def sync_get_room(user: User, other_user: User):
    room, _ = Room.objects.get_or_create( #type:ignore
            user1__in=[user, other_user],
            user2__in=[user, other_user],
            defaults={'user1': user, 'user2': other_user}
        )
    return room   



@sync_to_async
def get_room(user: User, other_user: User):
    room, _ = Room.objects.get_or_create(  # type:ignore
        user1__in=[user, other_user],
        user2__in=[user, other_user],
        defaults={'user1': user, 'user2': other_user}
    )
    return room


@sync_to_async
def validate_user(access_token):
    user = decode_token(access_token)
    if user:
        return user, True
    else:
        return None, False


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "chats"
        self.curr_room = None
        self.other_user = None
        query_params = self.scope['query_string'].decode('utf-8')
        self.access_token = query_params.split('=')[1]

        user, validation_res = await validate_user(self.access_token)
        if not validation_res:
            await self.close()
            return

        self.user = user

        # type:ignore
        await self.channel_layer.group_add("chats", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # type:ignore
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        type_of_msg = data["type"]

        if type_of_msg == "connect":
            email = data["email"]
            other_user, res = await get_user(email)
            if res:
                self.other_user = other_user
            else:
                await self.send(json.dumps({"error": "User not found"}))
                return
            room = await get_room(self.user, self.other_user)  # type:ignore
            self.room_name = f"room_{room.id}"
            self.curr_room = room
            msgs = await get_msgs(self.curr_room)
            # type:ignore
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.send(json.dumps({"type": "chat_history", "messages": msgs}))
            return

        elif type_of_msg == "text":
            text = data["text"]
            # type:ignore
            msg = await create_msg(self.curr_room, self.user, self.other_user, text)
            await self.channel_layer.group_send(  # type:ignore
                self.room_name,
                {
                    "type": "chat_message",
                    "message": msg
                }
            )

        elif type_of_msg == "doc":
            if not self.curr_room or not self.other_user:
                await self.send(json.dumps({"error": "Room not established"}))
                return
            file_data = data["file_data"]
            file_name = data["file_name"]
            # type:ignore
            msg = await create_document(self.curr_room, self.user, self.other_user, file_data, file_name)
            await self.channel_layer.group_send(  # type:ignore
                self.room_name,
                {
                    "type": "chat_message",
                    "message": msg
                }
            )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(json.dumps({"type": "new_message", "message": message}))
