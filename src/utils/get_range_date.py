import datetime


def get_range_days(date):
    convert_to_datetime = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    start_week = convert_to_datetime - datetime.timedelta(convert_to_datetime.weekday())
    end_week = start_week + datetime.timedelta(6)
    start_instance = datetime.date(start_week.year, start_week.month, start_week.day).strftime('%Y-%m-%d')
    end_instance = datetime.date(end_week.year, end_week.month, end_week.day).strftime('%Y-%m-%d')

    days = {
        "start_instance": start_instance,
        "end_instance": end_instance
    }
    return days