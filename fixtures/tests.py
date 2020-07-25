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
    variant = 'test'


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
