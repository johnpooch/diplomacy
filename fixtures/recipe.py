import os
import re

from django.utils.text import camel_case_to_spaces
from django.conf import settings

from core import models
from core.models.base import GameStatus


file_location = 'fixtures/games/'


class Game:

    class Nations:
        ENGLAND = 'England'
        FRANCE = 'France'
        GERMANY = 'Germany'
        AUSTRIA = 'Austria-Hungary'
        ITALY = 'Italy'
        RUSSIA = 'Russia'
        TURKEY = 'Turkey'

    game = None
    variant = None
    turn_number = None
    test_user_nation = None

    @property
    def name(self):
        return camel_case_to_spaces(self.__class__.__name__).capitalize()

    @property
    def description(self):
        return self.__class__.__doc__.strip()

    @property
    def file_location(self):
        location = '/'.join(
            [
                settings.BASE_DIR,
                'fixtures',
                'games',
                self.variant,
                self.game
            ]
        )
        if not os.path.isdir(location):
            raise ValueError(
                'f{location} not found.'
            )
        return location

    @property
    def files(self):
        location = self.file_location
        dir_list = os.listdir(self.file_location)
        dir_list.sort()
        files = []
        for f in dir_list:
            files.append('/'.join([location, f]))
            if f.startswith(self.turn_number):
                return files
        raise ValueError(
            f'No file found beginning with {self.turn_number}.'
        )

    def create_game(self, variant):
        return models.Game.objects.create(
            variant=variant,
            name=self.name,
            desciption=self.description,
            status=GameStatus.ACTIVE,
            num_players=7,
        )

    def create_turn_from_file(self, f, game):
        f = os.path.basename(f)  # just take filename
        turn_data = self.convert_file_name_to_turn_data(f)
        return models.Turn.objects.create(
            game=game,
            **turn_data,
        )

    def convert_file_name_to_turn_data(self, filename):
        regex = r'^\d{2}_(?P<season>spring|fall)_(?P<year>\d{4})_(?P<phase>[a-z_]*)'
        m = re.search(regex, filename)
        data = m.groupdict()
        data['year'] = int(data['year'])
        return data

    def bake(self, variant, log):
        log('Creating game \'{self.game_name}\'')
        game = self.create_game(variant)
        # Create turns - bulk create?
        for f in self.files:
            turn = self.create_turn_from_file(f, game)
            # TODO make a management tool to dump out a game as json data.

class Spring1900(Game):
    variant = 'standard'
    game = 'game_1'
