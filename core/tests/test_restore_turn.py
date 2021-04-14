from unittest.mock import patch

from django.core.management.base import CommandError
from django.test import TestCase

from core.models.base import GameStatus, Season
from core.tests import DiplomacyTestCaseMixin, ManagementCommandTestCaseMixin


input_path = 'builtins.input'
restore_path = 'core.models.Game.restore_turn'


class TestRestoreTurn(TestCase, DiplomacyTestCaseMixin, ManagementCommandTestCaseMixin):

    command = 'restore_turn'

    def setUp(self):
        self.create_test_game_full(status=GameStatus.ACTIVE)
        self.first_turn = self.create_test_turn(
            game=self.game,
            current_turn=False,
        )
        self.second_turn = self.create_test_turn(game=self.game, season=Season.FALL)

        # Patch restore_turn
        self.restore_patcher = patch(restore_path)
        self.restore_patch = self.restore_patcher.start()
        self.addCleanup(self.restore_patcher.stop)

    def test_no_turn(self):
        with self.assertRaises(CommandError):
            self.call_command()

    def test_turn_not_found(self):
        with self.assertRaises(CommandError):
            self.call_command(10000)

    def test_turn_is_current(self):
        with self.assertRaises(CommandError):
            self.call_command(self.second_turn.id)

    def test_game_not_active(self):
        self.game.status = GameStatus.PENDING
        self.game.save()
        with self.assertRaises(CommandError):
            self.call_command(self.first_turn.id)

    def test_reset_prompt_no(self):
        with patch(input_path, return_value='n'):
            self.call_command(self.first_turn.id)
        self.assertEqual(self.restore_patch.call_count, 0)

    def test_reset_prompt_yes(self):
        with patch(input_path, return_value='y'):
            self.call_command(self.first_turn.id)
        self.assertEqual(self.restore_patch.call_count, 1)

    def test_reset_no_input(self):
        self.call_command(self.first_turn.id, noinput=True)
        self.assertEqual(self.restore_patch.call_count, 1)
