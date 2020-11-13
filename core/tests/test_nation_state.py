from django.test import TestCase

from core import models
from core.tests import DiplomacyTestCaseMixin


class TestNationState(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(variant=self.variant)
        self.nation = self.create_test_nation(variant=self.variant)
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()

    def test_user_surrendering_no_user(self):
        nation_state = self.create_test_nation_state(
            turn=self.turn,
            nation=self.nation,
            user=None
        )
        self.assertFalse(nation_state.user_surrendering)

    def test_user_surrendering_not_surrendering(self):
        nation_state = self.create_test_nation_state(
            turn=self.turn,
            nation=self.nation,
            user=self.user,
        )
        self.assertFalse(nation_state.user_surrendering)

    def test_user_surrendering(self):
        nation_state = self.create_test_nation_state(
            turn=self.turn,
            nation=self.nation,
            user=self.user,
        )
        models.Surrender.objects.create(user=self.user, turn=self.turn)
        self.assertTrue(nation_state.user_surrendering)

    def test_civil_disorder_no_user(self):
        nation_state = self.create_test_nation_state(
            turn=self.turn,
            nation=self.nation,
            user=None,
        )
        models.Surrender.objects.create(user=self.user, turn=self.turn)
        self.assertTrue(nation_state.civil_disorder)

    def test_civil_disorder_user_surrendered(self):
        nation_state = self.create_test_nation_state(
            turn=self.turn,
            nation=self.nation,
            user=self.user,
        )
        models.Surrender.objects.create(user=self.user, turn=self.turn)
        self.assertTrue(nation_state.civil_disorder)
