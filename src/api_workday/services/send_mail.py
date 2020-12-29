from django.template.loader import render_to_string

from api_base.services.sendmail import SendMail
from django.conf import settings
from api_workday.constants import Workday
from django.shortcuts import render


class SendMailRequestOff:
    url_logo = 'http://{0}:{1}/static/paradoxlogo.png'.format(settings.API_HOST, settings.API_PORT)

    @classmethod
    def send_request(cls, type_off, name_admin, name_user, list_email, date_off=None):
        content = render_to_string('../templates/request_off.html',
                                   {'name_admin': name_admin, 'name_user': name_user, 'date_off': date_off,
                                    'link': settings.URL_WEB_INTERNAL, 'type_off': type_off, 'logo': cls.url_logo})
        if type_off.type == 1:
            title = 'Request Off(Insurance)'
            SendMail.start([settings.DEFAULT_EMAIL_ADMIN], title, content)
            return
        elif type_off.is_ot_days:
            title = 'Request OT'
        else:
            title = 'Request Off'

        SendMail.start(list_email, title, content)

    @classmethod
    def send_forward_request(cls, type_off, name_admin, name_admin_manage, name_user, email, date_off=None):
        content_user = render_to_string('../templates/forward_request_off.html',
                                        {'name_admin': name_admin, 'name_user': name_user,
                                         'name_admin_manage': name_admin_manage, 'logo': cls.url_logo})

        content_manage = render_to_string('../templates/forward_request_off_to_manage.html',
                                          {'name_admin': name_admin, 'name_user': name_user,
                                           'name_admin_manage': name_admin_manage, 'date_off': date_off,
                                           'link': settings.URL_WEB_INTERNAL, 'logo': cls.url_logo})

        if type_off.is_ot_days:
            title = 'Forward Request OT'
        else:
            title = 'Forward Request Off'
        SendMail.start(email['user'], title, content_user)
        SendMail.start(email['admin'], title, content_manage)

    @classmethod
    def send_reject_request(cls, type_off, name_user, name_admin, reason, list_email, list_email_admin=None,
                            date_off=None):
        content = render_to_string('../templates/reject_request_off.html',
                                   {'name_admin': name_admin, 'name_user': name_user,
                                    'reason': reason, 'logo': cls.url_logo})
        if list_email_admin is None:
            list_email_admin = []
        list_email_admin.append(settings.DEFAULT_EMAIL_ADMIN)

        if type_off.is_ot_days:
            title = 'Reject Request OT'
        elif type_off.type == 1:
            title = 'Reject Request Off(Insurance)'
        else:
            title = 'Reject Request Off'
        SendMail.start(list_email, title, content, cc=list_email_admin)

    @classmethod
    def send_approve_request_to_user(cls, type_off, name_user, name_admin, list_email, date_off=None):
        content = render_to_string('../templates/approve_request_off.html',
                                   {'name_admin': name_admin, 'name_user': name_user, 'date_off': date_off,
                                    'type_off': type_off, 'logo': cls.url_logo})
        if type_off.is_ot_days:
            title = 'Approve Request OT'
        elif type_off.type == 1:
            title = 'Approve off(Insurance)'
        else:
            title = 'Approve Request off'

        SendMail.start(list_email, title, content)

    @classmethod
    def send_approve_request_to_manage(cls, type_off, name_user, email_user, list_email, date_off=None):
        content = render_to_string('../templates/leave_notice.html',
                                   {'name_user': name_user, 'email_user': email_user, 'date_off': date_off,
                                    'type_off': type_off, 'logo': cls.url_logo})

        if type_off.is_ot_days:
            title = 'Approve Request OT'
        elif type_off.type == 1:
            title = 'Approve off(Insurance)'
        else:
            title = 'Approve Request off'

        SendMail.start(list_email, title, content, cc=[settings.DEFAULT_EMAIL_ADMIN])

    @classmethod
    def send_cancel_request(cls, type_off, name_user, list_email, date_off=None):
        content = render_to_string('../templates/cancel_notice.html',
                                   {'name_user': name_user, 'date_off': date_off, 'type_off': type_off,
                                    'logo': cls.url_logo})

        if type_off.is_ot_days:
            title = 'Cancel Request OT'
        elif type_off.type == 1:
            title = 'Cancel Request Off(Insurance)'
        else:
            title = 'Cancel Request Off'
        SendMail.start(list_email, title, content, cc=[settings.DEFAULT_EMAIL_ADMIN])
