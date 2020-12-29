from datetime import datetime

import jwt
from django.conf import settings
from rest_framework.exceptions import ValidationError

from api_base.services import BaseService


class TokenUtil(BaseService):

    @staticmethod
    def get_header():
        return {
            "alg": "HS256",
            "typ": "JWT"
        }

    @staticmethod
    def get_secret_key():
        return settings.SECRET_KEY

    @staticmethod
    def encode(user):
        payload = {
            "email": user.email,
            "iat": datetime.now().timestamp()
        }

        token = jwt.encode(payload, TokenUtil.get_secret_key(), algorithm='HS256')
        return token.decode("utf-8")

    @staticmethod
    def decode(token, token_hours=12):
        payload = jwt.decode(token, TokenUtil.get_secret_key(), algorithms=['HS256'])

        iat = int(payload.get("iat"))
        email = payload.get('email')

        if iat + token_hours * 60 * 60 < datetime.now().timestamp():
            return None

        from api_user.services import UserService
        user = UserService.get_user_by_email(email)
        if user:
            return user
        return None

    @staticmethod
    def verification_encode(name, email, phone, personal_email):
        payload = {
            "name": name,
            "email": email,
            "phone": phone,
            "personal_email": personal_email
        }
        token = jwt.encode(payload, TokenUtil.get_secret_key(), algorithm='HS256')
        return token.decode("utf-8")

    @staticmethod
    def verify(token):
        try:
            payload = jwt.decode(token, TokenUtil.get_secret_key(), algorithms=['HS256'])
            return {
                "name": payload.get('name'),
                "email": payload.get('email'),
                "phone": payload.get('phone'),
                "personal_email": payload.get('personal_email')
            }
        except:
            raise ValidationError('Invalid token')
