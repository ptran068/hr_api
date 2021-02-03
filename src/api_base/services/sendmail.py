#!/usr/bin/env python

# author Huy 
# date 8/19/2019

import threading

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.module_loading import import_string


class APIEmailMessage(EmailMessage):
    """
    Customize EmailMessage class to get mail username/password
    """

    def __init__(self, **kwargs):
        self.username = kwargs.pop('username', None)
        self.password = kwargs.pop('password', None)
        super().__init__(**kwargs)

    def get_connection(self, backend=None, fail_silently=False, **kwds):
        if not self.connection:
            klass = import_string(backend or settings.EMAIL_BACKEND)
            self.connection = klass(fail_silently=fail_silently, username=self.username, password=self.password, **kwds)
        return self.connection


class EmailThread(threading.Thread):
    def __init__(self, subject=None, content=None, email=None, sender=None, email_password=None, from_email=None, cc=None, bcc=None):
        self.subject = subject
        self.content = content
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL,
        self.sender = sender or settings.EMAIL_HOST_USER
        self.mail_password = email_password or settings.EMAIL_HOST_PASSWORD
        self.recipient_list = email
        self.cc = cc
        self.bcc = bcc
        threading.Thread.__init__(self)

    def run(self):
        email_options = dict(
            subject=self.subject,
            body=self.content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=self.recipient_list,
            username=self.sender,
            password=self.mail_password,
            cc=self.cc,
            bcc=self.bcc,
        )
        try:
            msg = APIEmailMessage(**email_options)
            msg.content_subtype = 'html'
            msg.send()
        except Exception as e:
            # TODO: Add a log right here
            print(str(e))


class SendMail:

    @staticmethod
    def start(email_list, subject, content, cc=None, bcc=None):
        EmailThread(subject=subject, email=email_list, content=content, cc=cc, bcc=bcc).start()
