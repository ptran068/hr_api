__author__ = "hoangnguyen"
__date__ = "$Feb 17, 2020 23:57:48 PM$"

from . import CustomBaseCommand
from .cmds import cmd_set_password


class Command(CustomBaseCommand):
    help = "All commands"
    validate_admin = True

    def add_arguments(self, parser):
        parser.add_argument('-set_password',
                            action='store_true',
                            default=False,
                            help='Update password')

    def handle_admin_access(self, *args, **options):
        if options.get('set_password'):
            cmd_set_password()
