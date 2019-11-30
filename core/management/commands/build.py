from django.core.management.base import BaseCommand

from core.factories import StandardGameFactory


class Command(BaseCommand):

    help = 'Command for creating a fixture of data for development.'

    def handle(self, *args, **options):
        StandardGameFactory()
