from rest_framework.mixins import ListModelMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .consumers import get_room, sync_get_room
from user.models import Messages
from .token_factory import create_token
from django.contrib.auth.models import User
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from .serializers import StaffSerializer
from rest_framework.permissions import IsAuthenticated, BasePermission
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import MsgSerializer


class ChatViewSet(ListModelMixin,GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = StaffSerializer


    def list(self, request, *args, **kwargs):
        all_users = User.objects.exclude(id = request.user.id)
        serializer = StaffSerializer(all_users,many=True)
        return Response(
            serializer.data
        )


    def create(self,request):
        patient = request.data.get("id")
        users = request.data.get("users").split(",")
        channel_layer = get_channel_layer()
        for user_email in users:
            try:
                user = User.objects.get(email=user_email) 
            except Exception as e:
                print(str(e))


            if user: #type:ignore
                room = sync_get_room(request.user,user)
                msg = Messages.objects.create( #type:ignore
                    room=room,
                    type="text",
                    text=patient,
                    sender=request.user,
                    receiver=user
                )
                print(msg)
                print(f"room_{room.id}")
                async_to_sync(channel_layer.group_send)( #type:ignore
                f"room_{room.id}", #type:ignore
                {
                    "type": "chat_message",
                    "message": MsgSerializer(msg).data 
                }
            )
        return Response(status=status.HTTP_201_CREATED)

class JwtToken(APIView):
    def post(self, request):
        email = request.data.get("username", None)
        password = request.data.get("password", None)
        if not email or not password:
            return Response(
                {"detail": "'username' and 'password' required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=email, password=password)
        if user and user.is_active:
            token = create_token(user)
            return Response(
                {
                    "token": token,
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invalid User"},
                status=status.HTTP_400_BAD_REQUEST
            )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_superuser


class Staff(ModelViewSet):
    queryset = User.objects.filter(is_staff=True, is_superuser=False)
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def create_user(self, username, password, email):
        user = User.objects.create_user(
            username=username, email=email, password=password, is_staff=True)
        user.save()

    def create(self, request):
        username = request.data.get("username", None)
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        if not username or not password:
            return Response(
                {"detail": "'username' and 'password' required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.create_user(username, password, email)
        return Response(
            status=status.HTTP_200_OK
        )
