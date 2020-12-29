import getpass
from django.core.management.base import BaseCommand


class CustomBaseCommand(BaseCommand):
    help = ""
    validate_admin = True

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        is_admin = False
        if self.validate_admin:
            password = getpass.getpass("Enter admin password: ")
            is_admin = password == 'ai123'
            if not is_admin:
                print("Wrong pass")
                return

        if is_admin:
            self.handle_admin_access(*args, **options)
        else:
            self.handle_user_access(*args, **options)
        print('*** DONE ***')

    def handle_admin_access(self, *args, **options):
        pass

    def handle_user_access(self, *args, **options):
        pass
