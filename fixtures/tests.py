from io import StringIO

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from core import models
from core.models.base import Phase, Season
from core.tests import DiplomacyTestCaseMixin
from .recipe import Game


class TestGame(Game):
    """
    Test docstring.
    """
    variant_identifier = 'test'
    year = 1901
    season = Season.FALL
    phase = Phase.BUILD


class TestRecipe(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        stdout = StringIO()
        self.recipe = TestGame(stdout.write)
        self.variant = models.Variant.objects.create(
            name='Test variant',
            identifier='test-variant',
        )

    def test_name(self):
        self.assertEqual(self.recipe.name, 'Test game')

    def test_description(self):
        self.assertEqual(self.recipe.description, 'Test docstring.')

    def test_file_location(self):
        self.recipe.game = 'game_1'
        self.assertEqual(
            self.recipe.fixture_location,
            settings.BASE_DIR + '/fixtures/fixtures/game_1'
        )

    def test_file_location_does_not_exist(self):
        self.recipe.game = 'fake_game'
        with self.assertRaises(ValueError):
            self.recipe.fixture_location,

    def test_files(self):
        self.recipe.variant = 'test'
        self.recipe.game = 'game_1'
        self.recipe.turn_number = '02'

    def test_populate_nation_map(self):
        nation = models.Nation.objects.create(
            variant=self.variant,
            name='England',
        )
        data = [
            {
                'pk': 10,
                'variant': 5,
                'name': 'England',
            }
        ]
        self.recipe._populate_nation_map(self.variant, data)
        self.assertEqual(self.recipe._nation_map[10], nation)

    def test_populate_territory_map(self):
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='London',
        )
        data = [
            {
                'pk': 10,
                'variant': 5,
                'name': 'London',
            }
        ]
        self.recipe._populate_territory_map(self.variant, data)
        self.assertEqual(self.recipe._territory_map[10], territory)

    def test_create_game(self):
        test_user = User.objects.create(
            username='some-test-user',
            email='some-test-user@test.com',
            password='pass'
        )
        game_data = {
            'pk': 9,
            'variant': 1,
            'name': 'Build Game',
            'description': 'Century themselves heavy.',
            'status': 'active',
            'private': False,
            'password': None,
            'order_deadline': 'twenty_four_hours',
            'retreat_deadline': 'twenty_four_hours',
            'build_deadline': 'twelve_hours',
            'process_on_finalized_orders': True,
            'nation_choice_mode': 'random',
            'num_players': 7,
            'created_by': test_user,
            'created_at': '2020-07-14T18:55:24.499Z',
            'initialized_at': '2020-07-14T18:55:24.802Z',
            'winners': []
        }
        game = self.recipe.create_game(self.variant, game_data)
        self.assertEqual(game.name, 'Test game')
        self.assertEqual(game.description, 'Test docstring.')
        self.assertEqual(game.variant, self.variant)

    def test_create_users(self):
        users = self.recipe.create_users(7)
        self.assertEqual(len(users), 7)
        self.assertEqual(users[-1].username, 'testuser')

    def test_create_turns(self):
        game = self.create_test_game(variant=self.variant)
        turn_data = [
            {
                'pk': 10,
                'game': 5,
                'season': 'fall',
                'phase': 'build',
                'year': 1901,
                'current_turn': True,
                'processed': False,
                'processed_at': None,
                'created_at': '2020-07-14T18:55:27.499Z'
            }
        ]
        turns = self.recipe.create_turns(game, turn_data)
        self.assertEqual(len(turns), 1)
        turn = turns[0]
        self.assertEqual(turn.game, game)
        self.assertEqual(turn.season, 'fall')
        self.assertEqual(self.recipe._turn_map[10], turn)

    def test_create_turn_end_turn_not_found(self):
        game = self.create_test_game(variant=self.variant)
        turn_data = [
            {
                'pk': 10,
                'game': 5,
                'season': 'fall',
                'phase': 'retreat_and_disband',
                'year': 1901,
                'current_turn': True,
                'processed': False,
                'processed_at': None,
                'created_at': '2020-07-14T18:55:27.499Z'
            }
        ]
        with self.assertRaises(ValueError):
            self.recipe.create_turns(game, turn_data)

    def test_validate(self):
        turn_data = [
            {
                'season': 'fall',
                'phase': 'retreat_and_disband',
                'year': 1901,
            }
        ]
        with self.assertRaises(ValueError):
            self.recipe.validate(turn_data)

    def test_create_pieces(self):
        game = self.create_test_game(variant=self.variant)
        nation = models.Nation.objects.create(
            variant=self.variant,
            name='England',
        )
        self.recipe._nation_map = {7: nation}
        piece_data = [
            {
                "pk": 67,
                "nation": 7,
                "game": 5,
                "type": "fleet",
                "turn_created": None,
                "turn_disbanded": None
            },
        ]
        piece = self.recipe.create_pieces(game, piece_data)[0]
        self.assertEqual(piece.nation, nation)
        self.assertEqual(piece.game, game)

    def test_create_pieces_discluded_because_of_turn(self):
        game = self.create_test_game(variant=self.variant)
        nation = models.Nation.objects.create(
            variant=self.variant,
            name='England',
        )
        self.recipe._nation_map = {7: nation}
        piece_data = [
            {
                "pk": 67,
                "nation": 7,
                "game": 5,
                "type": "fleet",
                "turn_created": 3,
                "turn_disbanded": None
            },
        ]
        pieces = self.recipe.create_pieces(game, piece_data)
        self.assertEqual(pieces, [])

    def test_create_piece_states(self):
        game = self.create_test_game(variant=self.variant)
        turn = models.Turn.objects.create(
            game=game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        nation = models.Nation.objects.create(
            variant=self.variant,
            name='England',
        )
        piece = models.Piece.objects.create(
            nation=nation,
            game=game,
        )
        dislodged_by = models.PieceState.objects.create(
            piece=piece,
            turn=turn,
        )
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='London',
        )
        attacker_territory = models.Territory.objects.create(
            variant=self.variant,
            name='Wales',
        )
        named_coast = models.NamedCoast.objects.create(
            parent=territory,
            name='London sc'
        )
        self.recipe._turn_map = {
            7: turn,
        }
        self.recipe._piece_map = {
            67: piece,
        }
        self.recipe._territory_map = {
            21: territory,
            22: attacker_territory,
        }
        self.recipe._named_coast_map = {
            225: named_coast,
        }
        self.recipe._piece_state_map = {
            68: dislodged_by,
        }
        piece_state_data = [
            {
                "pk": 133,
                "turn": 7,
                "piece": 67,
                "territory": 21,
                "named_coast": 225,
                "dislodged": False,
                "dislodged_by": 68,
                "destroyed": False,
                "destroyed_message": None,
                "must_retreat": False,
                "attacker_territory": 22
            }
        ]
        piece_state = self.recipe.create_piece_states(piece_state_data)[0]
        self.assertEqual(piece_state.piece, piece)
        self.assertEqual(piece_state.territory, territory)
        self.assertEqual(piece_state.named_coast, named_coast)
        self.assertEqual(piece_state.attacker_territory, attacker_territory)
        self.assertEqual(piece_state.dislodged_by, None)
        self.recipe.set_dislodged_by(piece_state_data)
        self.assertEqual(piece_state.dislodged_by, dislodged_by)

    def test_create_territory_states(self):
        game = self.create_test_game(variant=self.variant)
        turn = models.Turn.objects.create(
            game=game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        nation = models.Nation.objects.create(
            variant=self.variant,
            name='England',
        )
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='London',
        )
        self.recipe._turn_map = {
            7: turn,
        }
        self.recipe._territory_map = {
            1: territory,
        }
        self.recipe._nation_map = {
            2: nation,
        }
        territory_state_data = [
            {
                "pk": 133,
                "turn": 7,
                "territory": 1,
                "controlled_by": 2,
                "contested": False,
                "bounce_occurred": False
            }
        ]
        territory_state = self.recipe.create_territory_states(territory_state_data)[0]
        self.assertEqual(territory_state.turn, turn)
        self.assertEqual(territory_state.territory, territory)
        self.assertEqual(territory_state.controlled_by, nation)

    def test_create_nation_states_user_in_map(self):
        game = self.create_test_game(variant=self.variant)
        test_user = User.objects.create(
            username='some-test-user',
            email='some-test-user@test.com',
            password='pass'
        )
        turn = models.Turn.objects.create(
            game=game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        nation = models.Nation.objects.create(
            variant=self.variant,
            name='England',
        )
        self.recipe._turn_map = {
            7: turn,
        }
        self.recipe._user_map = {
            19: test_user,
        }
        self.recipe._nation_map = {
            3: nation,
        }
        nation_state_data = [
            {
                "pk": 24,
                "turn": 7,
                "nation": 3,
                "user": 19,
                "orders_finalized": False,
            }
        ]
        nation_state = self.recipe.create_nation_states(nation_state_data, [test_user])[0]
        self.assertEqual(nation_state.turn, turn)
        self.assertEqual(nation_state.nation, nation)
        self.assertEqual(nation_state.user, test_user)

    def test_create_nation_states_not_selected_nation(self):
        game = self.create_test_game(variant=self.variant)
        test_user_1 = User.objects.create(
            username='some-test-user',
            email='some-test-user@test.com',
            password='pass'
        )
        test_user_2 = User.objects.create(
            username='some-test-user2',
            email='some-test-user2@test.com',
            password='pass'
        )
        turn = models.Turn.objects.create(
            game=game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        nation = models.Nation.objects.create(
            variant=self.variant,
            name='England',
        )
        self.recipe._turn_map = {
            7: turn,
        }
        self.recipe._nation_map = {
            3: nation,
        }
        nation_state_data = [
            {
                "pk": 24,
                "turn": 7,
                "nation": 3,
                "user": 19,
                "orders_finalized": False,
            }
        ]
        nation_state = self.recipe.create_nation_states(
            nation_state_data,
            [test_user_1, test_user_2]
        )[0]
        self.assertEqual(nation_state.turn, turn)
        self.assertEqual(nation_state.nation, nation)
        self.assertEqual(nation_state.user, test_user_1)

    def test_create_nation_states_selected_nation(self):
        game = self.create_test_game(variant=self.variant)
        test_user_1 = User.objects.create(
            username='some-test-user',
            email='some-test-user@test.com',
            password='pass'
        )
        test_user_2 = User.objects.create(
            username='some-test-user2',
            email='some-test-user2@test.com',
            password='pass'
        )
        turn = models.Turn.objects.create(
            game=game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        nation = models.Nation.objects.create(
            variant=self.variant,
            name='England',
        )
        self.recipe._turn_map = {
            7: turn,
        }
        self.recipe._nation_map = {
            3: nation,
        }
        nation_state_data = [
            {
                "pk": 24,
                "turn": 7,
                "nation": 3,
                "user": 19,
                "orders_finalized": False,
            }
        ]
        self.recipe.test_user_nation = 'England'
        nation_state = self.recipe.create_nation_states(
            nation_state_data,
            [test_user_1, test_user_2]
        )[0]
        self.assertEqual(nation_state.turn, turn)
        self.assertEqual(nation_state.nation, nation)
        self.assertEqual(nation_state.user, test_user_2)
