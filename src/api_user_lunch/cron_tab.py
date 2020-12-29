from .services import UserLunchServices


def send_statistical_mail_by_week():
    return UserLunchServices.send_statistical_mail_by_week()

def send_statistical_mail_by_month():
    return UserLunchServices.send_statistical_mail_by_month()