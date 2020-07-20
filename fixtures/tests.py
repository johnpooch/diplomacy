from django.conf import settings
from django.test import TestCase

from core import models
from core.models.base import Phase, Season
from core.tests import DiplomacyTestCaseMixin
from .recipe import Game


class TestGameRecipe(Game):
    """
    Test docstring.
    """
    variant = 'test'


class TestRecipe(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.recipe = TestGameRecipe()

    def test_name(self):
        self.assertEqual(self.recipe.name, 'Test game recipe')

    def test_description(self):
        self.assertEqual(self.recipe.description, 'Test docstring.')

    def test_file_location(self):
        self.recipe.variant = 'test'
        self.recipe.game = 'game_1'
        self.assertEqual(
            self.recipe.file_location,
            settings.BASE_DIR + '/fixtures/games/test/game_1'
        )

    def test_file_location_does_not_exist(self):
        self.recipe.variant = 'test_fake'
        self.recipe.game = 'game_1'
        with self.assertRaises(ValueError):
            self.recipe.file_location,

    def test_files(self):
        self.recipe.variant = 'test'
        self.recipe.game = 'game_1'
        self.recipe.turn_number = '02'

    def test_convert_file_name_to_turn_data(self):
        file_name = '01_spring_1900_order'
        turn_data = self.recipe.convert_file_name_to_turn_data(file_name)
        self.assertEqual(turn_data['season'], Season.SPRING)
        self.assertEqual(turn_data['year'], 1900)
        self.assertEqual(turn_data['phase'], Phase.ORDER)

    def test_create_turn_from_file(self):
        f = 'test/location/01_spring_1900_order'  # prefix is removed
        game = self.create_test_game()
        turn = self.recipe.create_turn_from_file(f, game)
        self.assertEqual(type(turn), models.Turn)
        self.assertEqual(turn.game, game)
        self.assertEqual(turn.season, Season.SPRING)
        self.assertEqual(turn.phase, Phase.ORDER)
        self.assertEqual(turn.year, 1900)
