from unittest.mock import patch
from io import StringIO

from celery.result import AsyncResult
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from core import models
from core.models.base import GameStatus, Phase, Season


apply_async_path = 'core.tasks.process_turn.apply_async'
dummy_task_id = 'd095799e-fdad-4445-adeb-74a0c9d91a56'


class TestSetTurnEnd(TestCase):

    command = 'set_turn_end'
    date_format = '%Y-%m-%d %H:%M:%S'

    def setUp(self):
        self.out = StringIO()
        self.variant = models.Variant.objects.get(identifier='standard')
        self.game = models.Game.objects.create(
            name='Test game',
            variant=self.variant,
            num_players=7,
            created_by=None,
            status=GameStatus.ACTIVE,
        )
        self.turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.ORDER,
            season=Season.SPRING,
            year=1900,
        )
        self.tomorrow = timezone.now() + timezone.timedelta(days=1)
        self.tomorrow_string = self.tomorrow.strftime(self.date_format)
        self.yesterday = timezone.now() - timezone.timedelta(days=1)
        self.yesterday_string = self.yesterday.strftime(self.date_format)

        apply_async = patch(apply_async_path)
        self.apply_async = apply_async.start()
        self.apply_async.return_value = AsyncResult(id=dummy_task_id)

    def call_command(self, slug, date_string):
        call_command(self.command, slug, date_string, stdout=self.out)

    def test_command_invalid_slug(self):
        slug = 'some-slug'
        with self.assertRaises(CommandError):
            self.call_command(slug, self.tomorrow_string)

    def test_command_invalid_date_string(self):
        date_string = '20-20-10'
        with self.assertRaises(CommandError):
            self.call_command(self.game.slug, date_string)

    def test_command_past_date(self):
        with self.assertRaises(CommandError):
            self.call_command(self.game.slug, self.yesterday_string)

    def test_game_not_live(self):
        self.game.status = GameStatus.PENDING
        self.game.save()
        with self.assertRaises(CommandError):
            self.call_command(self.game.slug, self.tomorrow_string)

    def test_no_turn_end(self):
        current_turn = self.game.get_current_turn()
        self.assertIsNone(current_turn.turn_end)

        self.call_command(self.game.slug, self.tomorrow_string)
        current_turn.refresh_from_db()
        self.assertTrue(isinstance(current_turn.turn_end, models.TurnEnd))
        self.assertEqual(
            current_turn.turn_end.datetime.strftime(self.date_format),
            self.tomorrow_string
        )

    def test_existing_turn_end(self):
        current_turn = self.game.get_current_turn()
        hour_from_now = timezone.now() + timezone.timedelta(hours=1)
        models.TurnEnd.objects.new(current_turn, hour_from_now)

        self.call_command(self.game.slug, self.tomorrow_string)
        current_turn.refresh_from_db()
        self.assertTrue(isinstance(current_turn.turn_end, models.TurnEnd))
        self.assertEqual(
            current_turn.turn_end.datetime.strftime(self.date_format),
            self.tomorrow_string
        )
