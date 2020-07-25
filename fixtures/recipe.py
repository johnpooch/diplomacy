import json
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import camel_case_to_spaces

from core import models
from core.utils import faker as custom_faker


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
    turn_number = None
    test_user_nation = None

    def __init__(self, log):
        self.log = log
        self._turn_map = {}
        self._nation_map = {}
        self._territory_map = {}

    @property
    def name(self):
        return camel_case_to_spaces(self.__class__.__name__).capitalize()

    @property
    def description(self):
        return self.__class__.__doc__.strip()

    @property
    def fixture_location(self):
        location = '/'.join(
            [
                settings.BASE_DIR,
                'fixtures',
                'fixtures',
                self.game
            ]
        )
        if not os.path.isdir(location):
            raise ValueError(
                f'{location} not found.'
            )
        return location

    def get_fixture_file(self, file_name):
        path = '/'.join([self.fixture_location, file_name])
        if not os.path.isdir(path):
            raise ValueError(f'{path} not found.')
        return path

    def get_fixture_data(self, file_path):
        result = []
        with open(file_path) as json_file:
            data = json.load(json_file)
        for item in data:
            result.append({**data['fields'], 'pk': data['pk']})
        return result

    def create_users(self, num_players):
        users = [custom_faker.user() for i in range(num_players - 1)]
        test_user = User.objects.get_or_create(
            username='testuser',
            email='test-user@test.com',
            password='pass'
        )[0]
        users.append(test_user)
        return users

    def create_game(self, variant, data):
        data.update(
            {
                'variant': variant,
                'name': self.name,
                'description': self.description,
            }
        )
        data.pop('winners')
        data.pop('pk')
        game = models.Game.objects.create(**data)
        self.log(repr(game))
        return game

    def create_turns(self, game, data):
        result = []
        for item in data:
            item['game'] = game
            pk = item.pop('pk')
            turn = models.Turn.objects.create(**item)
            self.log(repr(turn))
            self._turn_map[pk] = turn
            result.append(turn)
        return result

    def bake(self, variant, log):
        game_data = self.get_fixture_data('game.json')[0]
        turn_data = self.get_fixture_data('turn.json')

        nation_data = self.get_fixture_data('nation.json')
        self._populate_nation_map(nation_data)

        self.log('Creating users for \'{self.game_name}\'...')
        users = self.create_users(game_data['num_players'])

        self.log('Creating game \'{self.game_name}\'...')
        game_data['created_by'] = users[-1]
        game = self.create_game(variant, game_data)

        self.log('Creating turns...')
        self.create_turns(game, turn_data)

        # TODO need to limit to only turns up to a given turn


    def _populate_nation_map(self, variant, data):
        for item in data:
            pk = item['pk']
            nation = models.Nation.objects.get(
                variant=variant,
                name=item['name']
            )
            self._nation_map[pk] = nation

    def _populate_territory_map(self, variant, data):
        for item in data:
            pk = item['pk']
            territory = models.Territory.objects.get(
                variant=variant,
                name=item['name']
            )
            self._territory_map[pk] = territory


class Spring1900(Game):
    game = 'game_1'
