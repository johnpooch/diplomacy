from django.test import TestCase

from core.models.base import DrawStatus
from core.game import expire_draws

from core.tests import DiplomacyTestCaseMixin


class TestDisbandPieces(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(variant=self.variant)
        self.turn = self.create_test_turn(game=self.game, processed=True)
        self.england = self.variant.nations.create(name='England')
        self.user = self.create_test_user()

    def test_expire_draws_no_draws(self):
        draws = expire_draws(self.turn)
        self.assertEqual(draws, [])

    def test_expire_draws(self):
        draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.england,
            proposed_by_user=self.user,
            status=DrawStatus.PROPOSED,
        )
        draws = expire_draws(self.turn)
        self.assertEqual(draws, [draw])
        self.assertEqual(draws[0].status, DrawStatus.EXPIRED)
