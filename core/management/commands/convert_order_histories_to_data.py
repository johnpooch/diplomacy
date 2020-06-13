import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from service.utils import text_to_orders

from core import models
from core.models import base
from core.utils import faker as custom_faker

fake = Faker()


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
        directory = settings.BASE_DIR + '/' + options['indir']

        if not os.path.isdir(directory):
            raise CommandError(f'"{directory}" not found.')

        with transaction.atomic():
            print(f'\nCreating new game from "{directory}"...')
            self.create_game()
            dir_list = os.listdir(directory)
            dir_list.sort()
            for filename in dir_list:
                file_location = directory + '/' + filename
                with open(file_location) as f:
                    text = (f.read())
                self.create_turn(filename, text)

    def create_game(self):
        self.users = [custom_faker.user() for i in range(7)]
        self.variant = models.Variant.objects.get(
            name='Standard',
        )
        self.game = models.Game.objects.create(
            variant=self.variant,
            name=custom_faker.word_name(),
            description=fake.sentence(),
            num_players=7,
            created_by=self.users[0],
            created_at=custom_faker.recent_date(),
        )
        self.game.participants.add(*self.users)
        self.game.initialize()

    def create_turn(self, filename, text):
        print(f'Converting \'{filename}\'...')
        regex = r'^\d{2}_(?P<season>spring|fall)_(?P<year>\d{4})_(?P<phase>[a-z_]*)'
        m = re.search(regex, filename)
        turn_data = m.groupdict()
        turn = models.Turn.objects.get(
            game=self.game,
            **turn_data,
        )
        orders = text_to_orders(text)
        for order in orders:
            order.turn = turn
            order.save()
        self.game.process()
