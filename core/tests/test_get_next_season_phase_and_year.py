from django.test import TestCase

from core import factories, models
from core.models.base import Phase, Season
from core.game import get_next_season_phase_and_year

from core.tests import DiplomacyTestCaseMixin


class TestGetNextSeasonPhaseAndYear(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = models.Variant.objects.get(identifier='standard')
        self.user = factories.UserFactory()
        self.game = models.Game.objects.create(
            name='Test game',
            variant=self.variant,
            num_players=7,
            created_by=self.user,
        )

    def test_turn_not_processed(self):
        old_turn = self.create_test_turn(game=self.game)
        with self.assertRaises(ValueError):
            get_next_season_phase_and_year(old_turn, None)

    def test_spring_order_to_retreat(self):
        old_turn = self.create_test_turn(game=self.game, processed=True)
        self.create_test_piece_state(turn=old_turn, dislodged=True)
        result = get_next_season_phase_and_year(old_turn, None)
        self.assertEqual(list(result), [Season.SPRING, Phase.RETREAT_AND_DISBAND, 1900])

    def test_spring_order_to_fall_order(self):
        old_turn = self.create_test_turn(game=self.game, processed=True)
        result = get_next_season_phase_and_year(old_turn, None)
        self.assertEqual(list(result), [Season.FALL, Phase.ORDER, 1900])

    def test_fall_order_to_retreat(self):
        old_turn = self.create_test_turn(game=self.game, processed=True, season=Season.FALL)
        self.create_test_piece_state(turn=old_turn, dislodged=True)
        result = get_next_season_phase_and_year(old_turn, None)
        self.assertEqual(list(result), [Season.FALL, Phase.RETREAT_AND_DISBAND, 1900])

    def test_fall_order_to_build_surplus(self):
        old_turn = self.create_test_turn(game=self.game, processed=True, season=Season.FALL)
        new_turn = self.create_test_turn(game=self.game)
        nation_state = self.create_test_nation_state(turn=new_turn)
        self.create_test_territory_state(turn=new_turn, controlled_by=nation_state.nation)
        result = get_next_season_phase_and_year(old_turn, new_turn)
        self.assertEqual(list(result), [Season.FALL, Phase.BUILD, 1900])

    def test_fall_order_to_spring_next_year(self):
        old_turn = self.create_test_turn(game=self.game, processed=True, season=Season.FALL)
        new_turn = self.create_test_turn(game=self.game)
        result = get_next_season_phase_and_year(old_turn, new_turn)
        self.assertEqual(list(result), [Season.SPRING, Phase.ORDER, 1901])
