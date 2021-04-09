from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.tests import DiplomacyTestCaseMixin


class TestAdvanceTurn(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        pass

    def test_warn_if_not_ready_to_process(self):
        with self.assertRaises(CommandError):
            pass
            # call_command('dump_game', game.id, self.test_dir, 'game_name')

    def test_warn_if_not_all_nations_have_given_orders(self):
        with self.assertRaises(CommandError):
            pass
            # call_command('dump_game', game.id, self.test_dir, 'game_name')

    def test_no_turn(self):
        pass

    def test_turn_not_found(self):
        pass

    def test_force(self):
        pass

    def test_dry_run(self):
        pass

    def test_real_run(self):
        pass