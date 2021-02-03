#!/usr/bin/env python

# author Huy
# date 8/14/2019

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError

from api_base.services import BaseService, TokenUtil, SendMail
from api_user.services import UserService


class LoginService(BaseService):
    """
    LOGIN METHOD
    """

    @classmethod
    def login(cls, **kwargs):
        try:
            email = kwargs.get('email')
            password = kwargs.get('password')
            user = UserService.get_user_by_email(email)
            if not user or not user.check_password(password):
                raise ValidationError("Invalid username or password")
            token = TokenUtil.encode(user)
            res = dict(
                success=True,
                token=token,
                user=user.id,
                profile_id=user.profile.id,
                email=user.email,
                active=user.active,
                admin=user.is_admin,
                image=None,
                pm=user.is_project_manager
            )
            if user.profile.image:
                res.update(image=settings.MEDIA_IMAGE + '/media/' + str(user.profile.image))
            return res
        except Exception as e:
            raise e

    @classmethod
    def forgot_password(cls, email):
        user = UserService.get_user_by_email(email)
        if user:
            token = TokenUtil.encode(user)
            link = f'http://{settings.UI_HOST}/resetPassword?token={token}'
            content = render_to_string('../templates/password_email.html', {'link': link})
            SendMail.start([email], 'Forgot Password', content)
            return True
        return False

    @classmethod
    def change_password(cls, user, password):
        user.password = make_password(password, salt=settings.SECRET_KEY)
        user.save()
