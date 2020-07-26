from copy import deepcopy
import json
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import camel_case_to_spaces

from core import models
from core.utils import faker as custom_faker


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
    test_user_nation = None
    year = None
    season = None
    phase = None

    def __init__(self, log):
        self.log = log
        self._turn_map = {}
        self._nation_map = {}
        self._territory_map = {}
        self._named_coast_map = {}
        self._piece_map = {}
        self._piece_state_map = {}
        self._user_map = {}

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
            if self._check_if_last_turn(item):
                return result
        raise ValueError(
            'Could not find turn in fixture with the given year, season and '
            'phase.'
        )

    def create_pieces(self, game, data):
        result = []
        for item in data:
            turn_created = item['turn_created']
            if turn_created and turn_created not in self._turn_map.keys():
                # this piece does not exist by this point in the game.
                continue
            item['game'] = game
            nation_pk = item['nation']
            item['nation'] = self._nation_map[nation_pk]
            pk = item.pop('pk')
            piece = models.Piece.objects.create(**item)
            self.log(repr(piece))
            self._piece_map[pk] = piece
            result.append(piece)
        return result

    def create_piece_states(self, data):
        copied_data = deepcopy(data)
        result = []
        for item in copied_data:
            turn_pk = item['turn']
            try:
                turn = self._turn_map[turn_pk]
            except KeyError:
                continue
            item['turn'] = turn

            piece_pk = item['piece']
            item['piece'] = self._piece_map[piece_pk]

            territory_pk = item['territory']
            item['territory'] = self._territory_map[territory_pk]

            named_coast_pk = item['named_coast']
            if named_coast_pk:
                item['named_coast'] = self._named_coast_map[named_coast_pk]

            item.pop('dislodged_by')

            attacker_territory_pk = item['attacker_territory']
            if attacker_territory_pk:
                item['attacker_territory'] = self._territory_map[attacker_territory_pk]

            pk = item.pop('pk')
            piece_state = models.PieceState.objects.create(**item)
            self._piece_state_map[pk] = piece_state
            self.log(repr(piece_state))
            result.append(piece_state)
        return result

    def create_territory_states(self, data):
        result = []
        for item in data:
            turn_pk = item['turn']
            try:
                turn = self._turn_map[turn_pk]
            except KeyError:
                continue
            item['turn'] = turn

            territory_pk = item['territory']
            item['territory'] = self._territory_map[territory_pk]

            controlled_by_pk = item['controlled_by']
            item['controlled_by'] = self._nation_map[controlled_by_pk]

            item.pop('pk')

            territory_state = models.TerritoryState.objects.create(**item)
            self.log(repr(territory_state))
            result.append(territory_state)
        return result

    def create_nation_states(self, data, users):
        result = []
        for item in data:
            turn_pk = item['turn']
            try:
                turn = self._turn_map[turn_pk]
            except KeyError:
                continue
            item['turn'] = turn

            nation_pk = item['nation']
            nation = self._nation_map[nation_pk]
            item['nation'] = nation

            user_pk = item['user']
            if user_pk in self._user_map.keys():
                user = self._user_map[user_pk]
            elif nation.name == self.test_user_nation:
                user = users[-1]
                self._user_map[user_pk] = user
            else:
                user = users.pop(0)
                self._user_map[user_pk] = user

            item['user'] = user

            item.pop('pk')

            nation_state = models.NationState.objects.create(**item)
            self.log(repr(nation_state))
            result.append(nation_state)
        return result

    def set_dislodged_by(self, data):
        for item in data:
            pk = item['pk']
            dislodged_by_pk = item['dislodged_by']
            if dislodged_by_pk:
                piece_state = self._piece_state_map[pk]
                dislodged_by = self._piece_state_map[dislodged_by_pk]
                piece_state.dislodged_by = dislodged_by
                piece_state.save()

    def validate(self, turn_data):
        if not any(
            [self._check_if_last_turn(item) for item in turn_data]
        ):
            raise ValueError(
                'Could not find turn in fixture with the given year, season '
                'and phase.'
            )

    def bake(self, variant, log):
        game_data = self.get_fixture_data('game.json')[0]
        turn_data = self.get_fixture_data('turn.json')
        nation_data = self.get_fixture_data('nation.json')
        territory_data = self.get_fixture_data('territory.json')
        named_coast_data = self.get_fixture_data('named_coast.json')
        piece_data = self.get_fixture_data('piece.json')
        piece_state_data = self.get_fixture_data('piece_state.json')
        territory_state_data = self.get_fixture_data('territory_state.json')
        nation_state_data = self.get_fixture_data('nation_state.json')

        self.validate(turn_data)

        self._populate_nation_map(nation_data)
        self._populate_territory_map(territory_data)
        self._populate_named_coast_map(named_coast_data)

        self.log('Creating users for \'{self.game_name}\'...')
        users = self.create_users(game_data['num_players'])

        self.log('Creating game \'{self.game_name}\'...')
        game_data['created_by'] = users[-1]
        game = self.create_game(variant, game_data)

        self.log('Creating turns...')
        self.create_turns(game, turn_data)

        self.log('Creating pieces...')
        self.create_pieces(game, piece_data)

        self.log('Creating piece states...')
        self.create_piece_states(piece_state_data)
        self.set_dislodged_by(piece_state_data)

        self.log('Creating territory states...')
        self.create_territory_states(territory_state_data)

        self.log('Creating nation states...')
        self.create_nation_states(nation_state_data, users)

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

    def _populate_named_coast_map(self, variant, data):
        for item in data:
            pk = item['pk']
            named_coast = models.NamedCoast.objects.get(
                parent__variant=variant,
                name=item['name']
            )
            self._named_coast_map[pk] = named_coast

    def _check_if_last_turn(self, data):
        return all(
            [
                data['season'] == self.season,
                data['phase'] == self.phase,
                data['year'] == self.year
            ]
        )


class TestGame(Game):
    """
    Test docstring.
    """
    variant = 'test'
    year = 1901
    season = Season.FALL
    phase = Phase.BUILD
