
from .services import EventServices


def get_birthday_events():
    return EventServices.get_birthday_events()

def reminder_admin_set_birthday_slack():
    return EventServices.reminder_admin_set_birthday_slack()
