from django.test import TestCase
from django.utils import timezone

from core.tests import DiplomacyTestCaseMixin


class TestNationState(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(variant=self.variant)
        self.nation = self.create_test_nation(variant=self.variant)
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()

    def create_nation_state(self, **kwargs):
        return self.create_test_nation_state(
            nation=self.nation,
            turn=self.turn,
            user=self.user,
            **kwargs,
        )

    def test_surrender_no_commit(self):
        nation_state = self.create_test_nation_state()
        nation_state.pk = None
        nation_state = nation_state.surrender(commit=False)
        self.assertIsNone(nation_state.pk)

    def test_surrender(self):
        nation_state = self.create_test_nation_state()
        nation_state = nation_state.surrender()
        self.assertTrue(nation_state.surrendered)
        self.assertTrue(nation_state.surrendered_at)

    def test_cancel_surrender_no_commit(self):
        nation_state = self.create_test_nation_state(
            surrendered=True,
            surrendered_at=timezone.now(),
        )
        nation_state.pk = None
        nation_state = nation_state.cancel_surrender(commit=False)
        self.assertIsNone(nation_state.pk)

    def test_cancel_surrender(self):
        nation_state = self.create_test_nation_state(
            surrendered=True,
            surrendered_at=timezone.now(),
        )
        nation_state = nation_state.cancel_surrender()
        self.assertFalse(nation_state.surrendered)
        self.assertIsNone(nation_state.surrendered_at)

    def test_toggle_surrender_not_current_turn(self):
        nation_state = self.create_test_nation_state()
        nation_state.turn.current_turn = False
        with self.assertRaises(ValueError):
            nation_state = nation_state.toggle_surrender()

    def test_toggle_surrender_not_surrendered(self):
        nation_state = self.create_test_nation_state()
        nation_state = nation_state.toggle_surrender()
        self.assertTrue(nation_state.surrendered)
        self.assertTrue(nation_state.surrendered_at)

    def test_toggle_surrender_surrendered(self):
        nation_state = self.create_test_nation_state(
            surrendered=True,
            surrendered_at=timezone.now(),
        )
        nation_state = nation_state.toggle_surrender()
        self.assertFalse(nation_state.surrendered)
        self.assertIsNone(nation_state.surrendered_at)
