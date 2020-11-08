import shlex
import subprocess
import sys
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import autoreload


class Command(BaseCommand):
    help = 'Starts a Celery worker for development.'
    # Validation is called explicitly each time the server is reloaded.
    requires_system_checks = False

    @staticmethod
    def start_celery(app):
        subprocess.call(shlex.split(f'celery worker -q -l info -A {app} -B'))

    @staticmethod
    def stop_celery():
        subprocess.call(shlex.split('pkill -2 celery'))

    def add_arguments(self, parser):
        parser.add_argument(
            '-A', '--app', type=str, dest='app_name', default='project',
            help='Set the app name.',
        )
        parser.add_argument(
            '--noreload', action='store_false', dest='use_reloader',
            help='Tells Celery to NOT use the auto-reloader.',
        )

    def handle(self, *args, **options):
        use_reloader = options['use_reloader']

        if use_reloader:
            autoreload.run_with_reloader(self.run, **options)
        else:
            self.run(**options)

    def run(self, **options):
        # If an exception was silenced in ManagementUtility.execute in order
        # to be raised in the child process, raise it now.
        autoreload.raise_last_exception()

        self.stdout.write('Performing system checks...\n\n')
        self.check(display_num_errors=True)
        self.check_migrations()

        now = datetime.now().strftime('%B %d, %Y - %X')
        self.stdout.write(now)

        try:
            self.stop_celery()
            self.start_celery(app=options['app_name'])
        except KeyboardInterrupt:
            self.stop_celery()
            sys.exit(0)

