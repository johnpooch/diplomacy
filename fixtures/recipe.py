import random

from django.utils.text import camel_case_to_spaces

from core import models
from core.models.base import GameStatus


file_location = ''


class Game:

    class Nations:
        ENGLAND = 'England'
        FRANCE = 'France'
        GERMANY = 'Germany'
        AUSTRIA = 'Austria-Hungary'
        ITALY = 'Italy'
        RUSSIA = 'Russia'
        TURKEY = 'Turkey'

    turn = None
    game = None
    test_user_nation = None

    @property
    def name(self):
        # TODO test
        return camel_case_to_spaces(self.__class__.__name__)

    @property
    def description(self):
        # TODO test
        return self.__class__.__doc__

    @property
    def files(self):
        directory = settings.BASE_DIR + '/' + file_location
        if not os.path.isdir(directory):
            raise CommandError(f'"{directory}" not found.')

    def create_game(self, variant):
        return models.Game.objects.create(
            variant=variant,
            name=self.name,
            desciption=self.description,
            status=GameStatus.ACTIVE,
            num_players=7,
        )

    def convert_file_name_to_turn_data(self, filename):
        regex = r'^\d{2}_(?P<season>spring|fall)_(?P<year>\d{4})_(?P<phase>[a-z_]*)'
        m = re.search(regex, filename)
        return = m.groupdict()

    def bake(self, variant, log):
        log('Creating game \'{self.game_name}\'')
        game = self.create_game(variant)
        # Create turns - bulk create?
