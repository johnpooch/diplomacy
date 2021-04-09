
from django.core.management.base import CommandError
from django.test import TestCase

from core.tests import DiplomacyTestCaseMixin, ManagementCommandTestCaseMixin
from core.models.base import GameStatus


class TestShowTurns(TestCase, DiplomacyTestCaseMixin, ManagementCommandTestCaseMixin):

    command = 'show_turns'

    def setUp(self):
        self.create_test_game_full()
        self.turn = self.create_test_turn(game=self.game)

    def test_no_game(self):
        with self.assertRaises(CommandError):
            self.call_command()

    def test_game_not_found(self):
        with self.assertRaises(CommandError):
            self.call_command('fake-game')

    def test_game_pending(self):
        with self.assertRaises(CommandError):
            self.call_command(self.game.slug)

    def test_show_turns_not_processed(self):
        self.game.status = GameStatus.ACTIVE
        self.game.save()
        output = self.call_command(self.game.slug)
        self.assertTrue('[ ]' in output)

    def test_show_turns_processed(self):
        self.game.status = GameStatus.ACTIVE
        self.game.save()
        self.turn.processed = True
        self.turn.save()
        output = self.call_command(self.game.slug)
        self.assertTrue('[x]' in output)
