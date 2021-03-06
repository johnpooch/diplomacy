import os
import shutil
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core import models
from core.management.commands.dump_game import Command as DumpGame
from core.tests import DiplomacyTestCaseMixin


class TestDumpGame(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.dump_game = DumpGame()
        self.test_dir = 'core/tests/test_dump_game_temp_dir'

        self.patcher_1 = patch(
            'django.core.management.commands.dumpdata.Command.execute',
        )
        self.mock_call_command = self.patcher_1.start()
        self.addCleanup(self.patcher_1.stop)
        self.location = '/'.join([settings.BASE_DIR, self.test_dir])
        self.create_temp_dir(self.location)

    def tearDown(self):
        self.delete_temp_dir(self.location)

    def create_temp_dir(self, location):
        os.makedirs(location)

    def delete_temp_dir(self, location):
        shutil.rmtree(location)

    def test_get_model_identifier(self):
        result = self.dump_game.get_model_identifier(models.Game)
        self.assertEqual(result, 'core.Game')

    def test_dump_model(self):
        game = self.create_test_game()
        game_location = '/'.join([self.location, 'game.json'])
        self.dump_game.dump_model(models.Game, [game.id], game_location)
        call = self.mock_call_command.call_args_list[0]
        args, kwargs = call
        self.assertEqual(args[0], 'core.Game')
        self.assertEqual(kwargs['indent'], 4)
        self.assertEqual(kwargs['primary_keys'], str(game.id))
        self.assertEqual(kwargs['output'], game_location)

    def test_handle_directory_does_not_exist(self):
        game = self.create_test_game()
        with self.assertRaises(CommandError):
            call_command('dump_game', game.id, 'some/fake/dir', '')

    def test_handle_game_directory_already_exists(self):
        game = self.create_test_game()
        self.create_temp_dir(self.location + '/game_name')
        with self.assertRaises(CommandError):
            call_command('dump_game', game.id, self.test_dir, 'game_name')
