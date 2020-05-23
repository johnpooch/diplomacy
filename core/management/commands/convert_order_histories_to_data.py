import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    @property
    def help(self):
        return 'Convert "playdiplomacy.com" order histories into data'

    def add_arguments(self, parser):
        parser.add_argument(
            'indir',
            type=str,
            help='Directory to load data from.',
        )

    def handle(self, *args, **options):
        in_dir = settings.BASE_DIR + '/' + options['indir']

        if not os.path.isdir(in_dir):
            raise CommandError(f'"{in_dir}" not found.')
        texts = self._get_texts(in_dir)
        orders = [self._convert_text_to_orders(t) for t in texts]

    @staticmethod
    def _get_texts(directory):
        texts = []
        for filename in os.listdir(directory):
            file_location = directory + '/' + filename
            with open(file_location) as f:
                texts.append(f.read())
        return texts

    @staticmethod
    def _convert_text_to_data(text):
        pass
