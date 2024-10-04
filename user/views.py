from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .token_factory import create_token



class JwtToken(APIView):
    def post(self,request):
        email = request.data.get("username",None)
        password = request.data.get("password",None)
        if not email or not password:
            return Response(
                {"detail" : "'username' and 'password' required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=email,password=password)
        if user and user.is_active:
            token = create_token(user)
            return Response(
                {
                    "token" : token,
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail" : "Invalid User"},
                status=status.HTTP_400_BAD_REQUEST
            )
