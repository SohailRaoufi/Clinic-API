from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .token_factory import create_token
from django.contrib.auth.models import User


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


class Staff(APIView):
    def create_user(self, username, password, email=None):
        user = User.objects.create_user(username, email, password)
        user.save()

    def post(self, request):
        username = request.data.get("username", None)
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        if not username or not password:
            return Response(
                {"detail": "'username' and 'password' required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.create_user(username, email, password)
        return Response(
            status=status.HTTP_200_OK
        )
