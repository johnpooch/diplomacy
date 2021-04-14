from unittest.mock import patch

from django.core.management.base import CommandError
from django.test import TestCase

from core.models.base import GameStatus
from core.tests import DiplomacyTestCaseMixin, ManagementCommandTestCaseMixin


input_path = 'builtins.input'
ready_to_process_path = 'core.models.Turn.ready_to_process'
process_turn_path = 'core.game.process_turn'


class TestAdvanceTurn(TestCase, DiplomacyTestCaseMixin, ManagementCommandTestCaseMixin):

    command = 'advance_turn'

    def setUp(self):
        self.create_test_game_full(status=GameStatus.ACTIVE)
        self.turn = self.create_test_turn(game=self.game)

        self.input_patcher = patch(input_path)
        self.input_patch = self.input_patcher.start()
        self.addCleanup(self.input_patcher.stop)

        self.ready_to_process_patcher = patch(ready_to_process_path)
        self.ready_to_process_patch = self.ready_to_process_patcher.start()
        self.ready_to_process_patch.return_value = True
        self.addCleanup(self.ready_to_process_patcher.stop)

        self.process_turn_patcher = patch(process_turn_path)
        self.process_turn_patch = self.process_turn_patcher.start()
        self.addCleanup(self.process_turn_patcher.stop)

    def test_warn_if_not_ready_to_process(self):
        self.ready_to_process_patch.return_value = False
        self.call_command(self.game.slug)
        self.assertTrue(self.input_patch.called)

    def test_game_not_found(self):
        with self.assertRaises(CommandError):
            self.call_command('fake-game')

    def test_no_input(self):
        self.ready_to_process_patch.return_value = False
        self.call_command(self.game.slug, '--no_input')
        self.assertFalse(self.input_patch.called)

    def test_dry_run(self):
        self.ready_to_process_patch.return_value = False
        self.process_turn_patch.return_value = {}
        self.call_command(self.game.slug, '--no_input', '--dry_run')
        self.assertFalse(self.input_patch.called)
        self.assertTrue(self.process_turn_patch.called_with(self.turn, True))

    def test_real_run(self):
        self.ready_to_process_patch.return_value = False
        self.process_turn_patch.return_value = {}
        self.call_command(self.game.slug, '--no_input')
        self.assertFalse(self.input_patch.called)
        self.assertTrue(self.process_turn_patch.called_with(self.turn, False))
