from .models import Lunch
from api_user_lunch.models import UserLunch 
import datetime
from api_user_lunch.services import UserLunchServices


class LunchServices:

    @classmethod
    def create(cls, serializer, provider):
        date = serializer.validated_data['date']
        if Lunch.objects.filter(date=date).exists():
            raise Exception(f'Lunch have been created with date {date}')
        lunch = serializer.save(provider_id=provider)
        UserLunch.objects.filter(date=date).update(lunch=lunch)
        return lunch

    @classmethod
    def create_many(cls, list_lunches):
        if not list_lunches:
            raise Exception('list_lunches are empty')
        expected_input = []
        get_lunches = Lunch.objects.all()
        expected_dates = [lunch.date for lunch in get_lunches]
        for lunch in list_lunches:
            list_dates = lunch.get('list_dates', [])
            list_dates = list(dict.fromkeys(list_dates))
            for date in list_dates:
                convert_to_datetime = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                if convert_to_datetime in expected_dates:
                    continue
                expected_dates.append(convert_to_datetime)
                expected_input.append(Lunch(
                    date=date,
                    has_veggie=lunch.get('has_veggie', False),
                    note=lunch.get('note', ''),
                    provider_id=lunch.get('provider', None),
                ))

        lunches = Lunch.objects.bulk_create(expected_input)
        for lunch_data in lunches:
            UserLunch.objects.filter(date=lunch_data.date).update(lunch=lunch_data)
        return lunches

    @classmethod
    def get_object(cls, pk):
        try:
            lunch = Lunch.objects.get(id=pk)
            return lunch
        except Lunch.DoesNotExist:
            raise Exception('lunch is empty')

    @classmethod
    def update(cls, serializer, pk, date):
        lunch_instance = cls.get_object(pk)
        get_lunch = Lunch.objects.filter(date=date).first()
        lunch_date = lunch_instance.date
        date_instance = datetime.date(lunch_date.year, lunch_date.month, lunch_date.day).strftime('%Y-%m-%d')
        if date and date != date_instance and get_lunch is not None:
            raise Exception(f'Lunch have been created with date {date}')
        return serializer.save()
