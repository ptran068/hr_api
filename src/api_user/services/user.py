import datetime
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.template.loader import render_to_string

from api_base.services import BaseService, TokenUtil, SendMail, Utils
from api_user.models import User, Profile
from api_workday.services.remain_leave import RemainLeaveService
from api_team.models import TeamMembers


class UserService(BaseService):

    @classmethod
    def get_filter_query(cls, request):
        query_email = request.query_params.get('email')
        query_gender = request.query_params.get('gender')
        query_title = request.query_params.get('title')
        query_name = request.query_params.get('name')
        query_team = request.query_params.get('team')
        query_birthday = request.query_params.get('birthday')
        query_joindate = request.query_params.get('joindate')
        query_active = request.query_params.get('active')
        filter_args = dict()
        if query_email is not None and query_email != '':
            filter_args.update(email__icontains=query_email)
        if query_name is not None and query_name != '':
            filter_args.update(profile__name__icontains=query_name)
        if query_gender is not None and query_gender != '':
            filter_args.update(profile__gender__istartswith=query_gender)
        if query_team not in (None, '', 'All', 'all'):
            members = TeamMembers.objects.select_related('team').filter(team__team_name=query_team).values_list('member_id', flat=True)
            filter_args.update(id__in=members)
        if query_title not in (None, '', 'All', 'all'):
            filter_args.update(title__istartswith=query_title)
        if query_birthday is not None and query_birthday != '':
            filter_args.update(profile__birth_day__month=query_birthday)
        if query_joindate:
            query_joindate = datetime.datetime.strptime(query_joindate, '%Y-%m')
            filter_args.update(profile__join_date__month=query_joindate.month, profile__join_date__year=query_joindate.year)
        if query_active is not None:
            filter_args.update(active=query_active)
        queryset = User.objects.select_related('profile').filter(**filter_args)
        return queryset

    @classmethod
    def get_user_by_id(cls, pk):
        user = User.objects.filter(pk=pk).first()
        return user

    @classmethod
    def get_user_by_email(cls, email):
        user = User.objects.filter(email=email).first()
        return user

    @classmethod
    def activate_user(cls, user):
        user.active = True
        user.save()

    @classmethod
    def deactivate_user(cls, user):
        user.active = False
        user.save()

    @classmethod
    def update_password(cls, data, user):
        try:
            current_password = data.get('current_password', None)
            hash_password = make_password(password=current_password, salt=settings.SECRET_KEY)
            if current_password is not None and current_password != "" and user.password != hash_password:
                raise Exception("Error: Password does not match")
            user.set_password(data.get('new_password'))
            return user
        except Exception:
            return None

    @classmethod
    def invite(cls, email, name):
        cls.send_mail(email=email, name=name, send_email=True)
        return {
            "success": True,
            "user": {
                'name': name,
                'email': email
            }
        }

    @classmethod
    def send_mail(cls, email=None, name=None, phone=None, personal_email=None, send_email=False):
        if send_email:
            token = TokenUtil.verification_encode(name, email, phone, personal_email)
            # TODO: Look at the link again
            link = f'http://{settings.UI_HOST}/verify?token={token}'
            content = render_to_string('../templates/invitation_email.html',
                                       {'name': name, 'email': email, 'link': link, 'token': token})
            SendMail.start([email, personal_email], 'Welcome to Company Management', content)

        if phone == "":
            phone = None
        email = email
        with transaction.atomic():
            user = User.objects.create_user(email=email, password='123456')
            profile = Profile.objects.create(user=user, name=name, phone=phone,
                                   personal_email=personal_email, join_date=datetime.datetime.now())
            RemainLeaveService.create_annual_leave(year=datetime.datetime.now().year, profile=profile)
