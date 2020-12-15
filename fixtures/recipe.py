from copy import deepcopy
import json
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import camel_case_to_spaces, slugify

from core import models
from core.models.base import Phase, Season
from core.utils import faker as custom_faker


ENGLAND = 'England'
FRANCE = 'France'
GERMANY = 'Germany'
AUSTRIA = 'Austria-Hungary'
ITALY = 'Italy'
RUSSIA = 'Russia'
TURKEY = 'Turkey'


class Game:

    variant_identifier = None
    game = None
    test_user_nation = None
    year = None
    season = None
    phase = None
    other_players_finalized = False

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
        if not os.path.isfile(path):
            raise ValueError(f'{path} not found.')
        return path

    def get_fixture_data(self, file_name):
        file_path = self.get_fixture_file(file_name)
        result = []
        with open(file_path) as json_file:
            data = json.load(json_file)
        for item in data:
            result.append({**item['fields'], 'pk': item['pk']})
        return result

    def create_users(self, num_players):
        users = [custom_faker.user() for i in range(num_players - 1)]
        try:
            test_user = User.objects.get(
                username='testuser',
                email='test-user@test.com',
            )
        except User.DoesNotExist:
            test_user = User.objects.create_user(
                username='testuser',
                email='test-user@test.com',
                password='pass',
            )
        users.append(test_user)
        return users

    def create_game(self, variant, data):
        data.update(
            {
                'variant': variant,
                'name': self.name,
                'slug': slugify(self.name),
                'description': self.description,
            }
        )
        data.pop('winners')
        data.pop('pk')
        game = models.Game.objects.create(**data)
        self.log('\t' + repr(game))
        return game

    def create_turns(self, game, data):
        result = []
        for item in data:
            item['game'] = game
            pk = item.pop('pk')
            turn = models.Turn.objects.create(**item)
            self.log('\t' + repr(turn))
            self._turn_map[pk] = turn
            result.append(turn)
            if self._check_if_last_turn(item):
                turn.current_turn = True
                turn.save()
                return result
        raise ValueError(
            'Could not find turn in fixture with the given year, season and '
            'phase.'
        )

    def create_pieces(self, game, data):
        result = []
        for item in data:
            turn_created = item['turn_created']
            if turn_created:
                try:
                    turn = self._turn_map[turn_created]
                    if turn.current_turn:
                        continue
                    item['turn_created'] = turn
                except KeyError:
                    # this piece does not exist by this point in the game.
                    continue
            item['game'] = game
            nation_pk = item['nation']
            item['nation'] = self._nation_map[nation_pk]

            turn_disbanded_pk = item['turn_disbanded']
            if turn_disbanded_pk:
                try:
                    item['turn_disbanded'] = self._turn_map[turn_disbanded_pk]
                except KeyError:
                    item['turn_disbanded'] = None

            pk = item.pop('pk')
            piece = models.Piece.objects.create(**item)
            self.log('\t' + repr(piece))
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
            try:
                item['piece'] = self._piece_map[piece_pk]
            except KeyError:
                # piece doesnt exist yet because build phase?
                continue

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
            self.log('\t' + repr(piece_state))
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
            if controlled_by_pk:
                item['controlled_by'] = self._nation_map[controlled_by_pk]

            item.pop('pk')

            territory_state = models.TerritoryState.objects.create(**item)
            self.log('\t' + repr(territory_state))
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
            test_nation = nation.name == self.test_user_nation
            item['nation'] = nation

            user_pk = item['user']
            if user_pk in self._user_map.keys():
                user = self._user_map[user_pk]
            elif test_nation:
                user = users[-1]
                self._user_map[user_pk] = user
            else:
                user = users.pop(0)
                self._user_map[user_pk] = user

            if turn.current_turn:
                if self.other_players_finalized and not test_nation:
                    item['orders_finalized'] = True
                else:
                    item['orders_finalized'] = False
            else:
                item['orders_finalized'] = True

            item['user'] = user

            item.pop('pk')

            nation_state = models.NationState.objects.create(**item)
            self.log('\t' + repr(nation_state))
            result.append(nation_state)
        return result

    def create_orders(self, data):
        result = []
        for item in data:
            turn_pk = item['turn']
            try:
                turn = self._turn_map[turn_pk]
            except KeyError:
                continue
            item['turn'] = turn

            nation = item['nation']
            item['nation'] = self._nation_map[nation]

            source = item['source']
            if source:
                item['source'] = self._territory_map[source]

            target = item['target']
            if target:
                item['target'] = self._territory_map[target]

            aux = item['aux']
            if aux:
                item['aux'] = self._territory_map[aux]

            target_coast = item['target_coast']
            if target_coast:
                item['target_coast'] = self._named_coast_map[target_coast]

            item.pop('pk')

            order = models.Order.objects.create(**item)
            self.log('\t' + repr(order))
            result.append(order)
        return result

    def set_dislodged_by(self, data):
        for item in data:
            turn_pk = item['turn']
            if turn_pk not in self._turn_map:
                continue
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

    def bake(self, variant):
        game_data = self.get_fixture_data('game.json')[0]
        turn_data = self.get_fixture_data('turn.json')
        nation_data = self.get_fixture_data('nation.json')
        territory_data = self.get_fixture_data('territory.json')
        named_coast_data = self.get_fixture_data('named_coast.json')
        piece_data = self.get_fixture_data('piece.json')
        piece_state_data = self.get_fixture_data('piece_state.json')
        territory_state_data = self.get_fixture_data('territory_state.json')
        nation_state_data = self.get_fixture_data('nation_state.json')
        order_data = self.get_fixture_data('order.json')

        self.validate(turn_data)

        self._populate_nation_map(variant, nation_data)
        self._populate_territory_map(variant, territory_data)
        self._populate_named_coast_map(variant, named_coast_data)

        self.log(f'Creating users for \'{self.name}\'...')
        users = self.create_users(game_data['num_players'])

        self.log(f'Creating game \'{self.name}\'...')
        game_data['created_by'] = users[-1]
        game = self.create_game(variant, game_data)

        game.participants.set(users)

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

        self.log('Creating orders...')
        self.create_orders(order_data)

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


class StandardGame(Game):
    game = 'game_1'
    variant_identifier = 'standard'


class FirstTurn(StandardGame):
    """
    This game has just started. Test user is playing as England.
    """
    game = 'game_1'
    variant_identifier = 'standard'
    year = 1901
    season = Season.SPRING
    phase = Phase.ORDER
    test_user_nation = ENGLAND


class FirstTurnAllOthersFinalized(FirstTurn):
    """
    This game has just started. All other players have finalized orders. Test
    user is playing as England.
    """
    other_players_finalized = True


class RetreatTurn(StandardGame):
    """
    Test user is playing as Austria-Hungary and must retreat one piece.
    """
    year = 1901
    season = Season.FALL
    phase = Phase.RETREAT_AND_DISBAND
    test_user_nation = AUSTRIA


class RetreatTurnAllOthersFinalized(RetreatTurn):
    """
    Test user is playing as Austria-Hungary and must retreat one piece. All
    other players have finalized their orders.
    """
    other_players_finalized = True


class BuildTurn(StandardGame):
    """
    Test user is playing as Germany and can build three pieces.
    """
    year = 1901
    season = Season.FALL
    phase = Phase.BUILD
    test_user_nation = GERMANY


class BuildTurnAllOthersFinalized(BuildTurn):
    """
    Test user is playing as Germany and can build three pieces. All other
    players have finalized their orders.
    """
    other_players_finalized = True


class DisbandTurn(StandardGame):
    """
    Test user is playing as England and must disband a piece.
    """
    year = 1902
    season = Season.FALL
    phase = Phase.BUILD
    test_user_nation = ENGLAND


class DisbandTurnAllOthersFinalized(DisbandTurn):
    """
    Test user is playing as England and must disband a piece. All other
    players have finalized their orders.
    """
    other_players_finalized = True


class MoveToNamedCoast(StandardGame):
    """
    Test user is playing as Italy and has a fleet in the Western-Mediterranean
    which can move to Spain.
    """
    year = 1902
    season = Season.FALL
    phase = Phase.ORDER
    test_user_nation = ITALY


class MoveToNamedCoastAllOthersFinalized(MoveToNamedCoast):
    """
    Test user is playing as Italy and has a fleet in the Western-Mediterranean
    which can move to Spain. All other players have finalized orders
    """
    other_players_finalized = True


recipes = {
    'first_turn': FirstTurn,
    'first_all_others_finalized': FirstTurnAllOthersFinalized,
    'retreat_turn': RetreatTurn,
    'retreat_turn_all_others_finalized': RetreatTurnAllOthersFinalized,
    'build_turn': BuildTurn,
    'build_turn_all_others_finalized': BuildTurnAllOthersFinalized,
    'disband_turn': DisbandTurn,
    'disband_turn_all_others_finalized': DisbandTurnAllOthersFinalized,
    'move_to_named_coast': MoveToNamedCoast,
    'move_to_named_coast_all_others_finalized': MoveToNamedCoastAllOthersFinalized,
}
