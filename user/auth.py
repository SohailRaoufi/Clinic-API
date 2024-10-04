from rest_framework.authentication import BaseAuthentication
from .token_factory import decode_token


class JwtAuth(BaseAuthentication):
    def authenticate(self, request):
        token : str | None= request.META.get("HTTP_AUTHORIZATION",None)
        if not token:
            return None

        # if it crashes it crashes lol
        try:
            token = token[7:]
        except IndexError:
            return None
        user = decode_token(token)
        if user:
            return user,None
        return None
