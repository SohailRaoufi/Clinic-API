from datetime import datetime,timedelta
from django.conf import settings
from django.contrib.auth.models import User
import jwt
from patient.utils import get_role

def create_token(user : User):
    data = {
        "user_id" : user.pk,
        "is_admin" : user.is_superuser,
        "role" : get_role(user), 
        "email" : user.email,
        "exp" : datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION_TIME)
    }

    return jwt.encode(data,settings.SECRET_KEY,algorithm="HS256")


def decode_token(token):
    try:
        data = jwt.decode(token,settings.SECRET_KEY,algorithms="HS256")
        user_id = data.get("user_id",None)
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
