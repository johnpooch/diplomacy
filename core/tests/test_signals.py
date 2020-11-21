from django.test import TestCase

from core.models.base import DrawStatus, GameStatus
from core.tests import DiplomacyTestCaseMixin


class TestSignals(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(
            variant=self.variant,
            status=GameStatus.ACTIVE,
        )
        self.england = self.create_test_nation(
            variant=self.variant,
            name='England'
        )
        self.france = self.create_test_nation(
            variant=self.variant,
            name='France'
        )
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()

    def test_winners_are_set_if_draw_accepted(self):
        draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.england,
            proposed_by_user=self.user,
        )
        draw.nations.set([self.france])
        self.assertEqual(self.game.status, GameStatus.ACTIVE)
        self.assertEqual(self.game.winners.all().count(), 0)
        draw.status = DrawStatus.ACCEPTED
        draw.save()

        self.assertEqual(self.game.status, GameStatus.ENDED)
        self.assertTrue(self.france in self.game.winners.all())
        self.assertTrue(self.england in self.game.winners.all())

    def test_winners_not_set_if_draw_rejected(self):
        draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.england,
            proposed_by_user=self.user,
        )
        draw.nations.set([self.france])
        draw.status = DrawStatus.REJECTED
        draw.save()
        self.assertEqual(self.game.status, GameStatus.ACTIVE)
        self.assertEqual(self.game.winners.all().count(), 0)

    def test_winners_not_set_if_draw_already_ended(self):
        self.game.winners.add(self.england)
        self.game.status = GameStatus.ENDED
        self.game.save()
        draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.england,
            proposed_by_user=self.user,
        )
        draw.nations.set([self.france])
        draw.status = DrawStatus.ACCEPTED
        draw.save()

        self.assertEqual(self.game.status, GameStatus.ENDED)
        self.assertFalse(self.france in self.game.winners.all())
        self.assertTrue(self.england in self.game.winners.all())
