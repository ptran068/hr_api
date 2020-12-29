__author__ = "hoangnguyen"
__date__ = "$Feb 17, 2020 23:57:48 PM$"

from django.contrib.auth.hashers import make_password
from rest_framework import exceptions

from api_base.errors import AuthErr
from api_user.services import UserService


def cmd_set_password():
    user_id = input("Enter user ID: ")
    pwd = input("Enter a new password: ")
    try:
        if len(pwd) < 6:
            error = AuthErr.PASSWORD_REQUIRED_CHARACTERS
            raise exceptions.ValidationError({'code': error.get('code'), 'message': error.get('message')})
        user = UserService.get_user_by_id(user_id)
        if user:
            user.password = make_password(pwd)
            user.save()
        else:
            raise Exception(f"No user with id {user_id}")
    except Exception as e:
        print(str(e))
