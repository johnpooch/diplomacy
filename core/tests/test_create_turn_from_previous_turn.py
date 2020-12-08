from django.test import TestCase

from core import models
from core.models.base import Phase, Season
from core.game import create_turn_from_previous_turn

from core.tests import DiplomacyTestCaseMixin


class TestCreateTurnFromPreviousTurn(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(variant=self.variant)
        self.turn = self.create_test_turn(
            game=self.game,
            processed=True,
            next_phase=Phase.ORDER,
            next_season=Season.FALL,
            next_year=1900,
        )
        self.patch_process_turn_apply_async()

    def test_new_turn_correct_season_phase_year(self):
        new_turn = create_turn_from_previous_turn(self.turn)
        self.assertEqual(models.Turn.objects.all().count(), 2)
        self.assertEqual(new_turn.phase, Phase.ORDER)
        self.assertEqual(new_turn.season, Season.FALL)
        self.assertEqual(new_turn.year, 1900)
