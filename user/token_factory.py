from datetime import datetime,timedelta
from django.conf import settings
from django.contrib.auth.models import User
import jwt

def create_token(user : User):
    data = {
        "user_id" : user.pk,
        "is_admin" : user.is_superuser,
        "email" : user.email,
        "exp" : datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION_TIME)
    }

    return jwt.encode(data,settings.SECRET_KEY,algorithm="HS256")


def decode_token(token):
    try:
        data = jwt.decode(token,settings.SECRET_KEY,algorithms="HS256")
        print(f"data {data}")
        user_id = data.get("user_id",None)
        print(f"user_id {user_id}")
        if not user_id:
            return None
        return User.objects.get(id=user_id)
    except(
        jwt.ExpiredSignatureError,
        jwt.DecodeError,
        jwt.InvalidTokenError,
        User.DoesNotExist,
    ) as e:
        print(e)
        return None
