from .models import Lunch
from api_user_lunch.models import UserLunch
import datetime
from lunarcalendar import Converter, Solar
from api_providers.models import Provider
from django.forms.models import model_to_dict
from api_base.services import SendMail
from django.template.loader import render_to_string
from calendar import monthrange
from utils.get_admins import get_all_admins
from utils.get_range_date import get_range_days


class UserLunchServices:
    @classmethod
    def get_users_lunch(cls, profile):
        users_lunch = UserLunch.objects.filter(profile=profile)
        if not users_lunch.exists():
            return []
        return users_lunch

    @classmethod
    def create(cls, serializer, profile, date):
        lunch = Lunch.objects.filter(date=date).first()
        today = datetime.date.today()
        convert_to_datetime = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        week_day = convert_to_datetime.weekday()
        if cls.is_weekday(day=week_day):
            raise Exception('Cant set lunch at weekend')
        if datetime.datetime.strptime(str(today), "%Y-%m-%d") <= datetime.datetime.strptime(str(date), "%Y-%m-%d"):
            if UserLunch.objects.filter(date=date, profile=profile).exists():
                raise Exception(f'user_lunch have been created with date {date}')
            return serializer.save(profile=profile, lunch=lunch)
        raise Exception('Create Error')

    @classmethod
    def create_many(cls, data, list_dates, profile):
        list_user_lunches = []
        if not list_dates:
            raise Exception('list_dates are empty')
        today = datetime.date.today()
        for date in list_dates:
            convert_to_datetime = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            week_day = convert_to_datetime.weekday()
            if cls.is_weekday(day=week_day):
                continue
            if datetime.datetime.strptime(str(today), "%Y-%m-%d") <= datetime.datetime.strptime(str(date), "%Y-%m-%d"):
                lunch = Lunch.objects.filter(date=date).first()
                user_lunch = UserLunch.objects.filter(date=date, profile=profile)
                if not user_lunch.exists():
                    list_user_lunches.append(
                        UserLunch(date=date, profile=profile, lunch=lunch, has_veggie=data.get('has_veggie')))
        return UserLunch.objects.bulk_create(list_user_lunches)

    @classmethod
    def create_many_by_admin(cls, list_data, profile):
        if not list_data:
            raise Exception('list_data is empty')
        list_user_lunches = []
        for data in list_data:
            lunch = Lunch.objects.filter(date=data['date']).first()
            list_user_lunches.append(
                UserLunch(date=data['date'], profile=profile, lunch=lunch, has_veggie=data['has_veggie']))
        return UserLunch.objects.bulk_create(list_user_lunches)

    @classmethod
    def is_lunar_day(cls, date):
        solar = Solar(date.year, date.month, date.day)
        lunar = Converter.Solar2Lunar(solar)
        if lunar.day == 1 or lunar.day == 15:
            return True
        return False

    @classmethod
    def is_weekday(cls, day):
        if day == 5 or day == 6:
            return True
        return False

    @classmethod
    def set_veggie(cls, profile):
        now = datetime.datetime.now()
        last_day = now.replace(day=monthrange(now.year, now.month)[1])
        list_existed_lunar = []
        user_lunches = UserLunch.objects.filter(date__gte=now, date__lte=last_day, profile=profile).values_list('date', flat=True)
        if not user_lunches.exists():
            list_user_lunches = []
            list_lunar_days = []
            step = datetime.timedelta(days=1)
            while now <= last_day:
                lunch = Lunch.objects.filter(date=now).first()
                week_day = now.weekday()
                if cls.is_weekday(day=week_day):
                    now += step
                    continue
                if cls.is_lunar_day(date=now):
                    list_lunar_days.append(now)
                    list_user_lunches.append(UserLunch(date=now, profile=profile, lunch=lunch, has_veggie=True))
                now += step
            if not list_lunar_days:
                raise Exception('Not found lunar day')
            return UserLunch.objects.bulk_create(list_user_lunches)
        for date in user_lunches:
            if cls.is_lunar_day(date=date):
                list_existed_lunar.append(date)
        UserLunch.objects.filter(profile=profile, date__in=list_existed_lunar).update(has_veggie=True)
        if not list_existed_lunar:
            raise Exception('Not found lunar day')
        return

    @classmethod
    def get_object(cls, pk):
        try:
            user_lunch = UserLunch.objects.get(id=pk)
            return user_lunch
        except UserLunch.DoesNotExist:
            raise Exception('user_lunch is empty')

    @classmethod
    def update(cls, serializer, pk, date):
        user_lunch_instance = cls.get_object(pk)
        get_user_lunch = UserLunch.objects.filter(date=date).first()
        lunch_date = user_lunch_instance.date
        date_instance = datetime.date(lunch_date.year, lunch_date.month, lunch_date.day).strftime('%Y-%m-%d')
        if date and date != date_instance and get_user_lunch is not None:
            raise Exception(f'user_lunch have been updated with date {date}')
        return serializer.save()

    @classmethod
    def delete(cls, pk):
        today = datetime.date.today()
        lunch = UserLunch.objects.filter(id=pk, date__gte=today)
        if not lunch.exists():
            raise Exception('Cant delete lunch with date lunch little than now')
        return lunch.delete()

    @classmethod
    def prepare_statistic_data(cls, is_month, date):
        k = 0
        convert_to_datetime = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        days = get_range_days(date=date)
        list_providers = Provider.objects.filter()
        if not list_providers:
            raise Exception('Have no provider')
        data = [None] * len(list_providers)
        for provider in list_providers:
            total_normal_lunch = []
            total_veggie_lunch = []
            lunches = Lunch.objects.filter(provider=provider,
                                           date__range=[days["start_instance"], days["end_instance"]])
            user_lunches = UserLunch.objects.filter(lunch__in=lunches,
                                                    date__range=[days["start_instance"], days["end_instance"]])
            if is_month:
                lunches = Lunch.objects.filter(provider=provider, date__month=convert_to_datetime.month,
                                               date__year=convert_to_datetime.year)
                user_lunches = UserLunch.objects.filter(lunch__in=lunches, date__month=convert_to_datetime.month,
                                                        date__year=convert_to_datetime.year)
            if not lunches.exists() or not user_lunches.exists():
                continue
            for user_lunch in user_lunches.values():
                if not user_lunch['has_veggie']:
                    total_normal_lunch.append(user_lunch)
                else:
                    total_veggie_lunch.append(user_lunch)
            data[k] = {
                'provider': model_to_dict(provider),
                'total_budgets': int(provider.budget) * len(user_lunches),
                'total_lunches': len(lunches.values()),
                'total_user_lunches': len(user_lunches.values()),
                'total_normal_lunch': len(total_normal_lunch),
                'total_veggie_lunch': len(total_veggie_lunch)
            }
            k += 1

        results = filter(lambda x: x is not None, data)
        return list(results)

    @classmethod
    def statistic(cls, is_month, date):
        data = cls.prepare_statistic_data(
            is_month=is_month,
            date=date
        )
        return data

    @classmethod
    def mail_helper(cls, is_month):
        users = get_all_admins()
        today = datetime.date.today()
        date = datetime.date(today.year, today.month, today.day).strftime('%Y-%m-%d')
        list_users = []
        for user in users.values_list("email"):
            list_users.append(user[0])
        data = cls.statistic(
            is_month=is_month,
            date=date
        )
        content = render_to_string('../templates/mailer/statistic_lunch.html', {'list_data': data})

        return SendMail.start(
            email_list=list_users,
            subject='Statistic annual lunch ',
            content=content
        )

    @classmethod
    def send_statistical_mail_by_week(cls):
        mail = cls.mail_helper(is_month=None)
        return mail

    @classmethod
    def send_statistical_mail_by_month(cls):
        mail = cls.mail_helper(is_month=True)
        return mail
