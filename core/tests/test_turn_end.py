from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from core import factories, models
from core.tasks import process_turn
from core.tests import DiplomacyTestCaseMixin
from core.models.base import DeadlineFrequency, Phase, Season


process_path = 'core.tasks._process_turn'


class TestTurnEnd(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = models.Variant.objects.get(id='standard')
        self.user = factories.UserFactory()
        self.game = models.Game.objects.create(
            name='Test game',
            variant=self.variant,
            num_players=7,
            created_by=self.user,
            order_deadline=DeadlineFrequency.TWENTY_FOUR_HOURS,
            retreat_deadline=DeadlineFrequency.TWELVE_HOURS,
            build_deadline=DeadlineFrequency.TWELVE_HOURS,
        )
        self.patch_process_turn_apply_async()
        self.patch_revoke_task_on_delete()

    def create_turn(self):
        return models.Turn.objects.create(
            game=self.game,
            phase=Phase.ORDER,
            season=Season.SPRING,
            year=1900,
        )

    def test_no_turn_end_on_created_turn(self):
        turn = self.create_turn()
        self.assertEqual(0, len(models.TurnEnd.objects.all()))
        self.assertIsNone(turn.turn_end)

    def test_turn_end_creation(self):
        turn = self.create_turn()
        datetime = timezone.now()

        turn_end = models.TurnEnd.objects.new(turn=turn, datetime=datetime)
        self.assertIsInstance(turn_end, models.TurnEnd)
        self.assertEqual(self.dummy_task_id, turn_end.task_id)

        self.apply_async.assert_called_with(
            kwargs={'turn_id': turn.id, 'processed_at': datetime},
            eta=datetime,
        )
        self.assertEqual(turn_end, turn.turn_end)

    def test_process_outcome(self):
        turn = self.create_turn()
        datetime = timezone.now()

        models.TurnEnd.objects.new(turn=turn, datetime=datetime)

        process_turn(turn_id=turn.id, processed_at=datetime)
        turn.refresh_from_db()

        self.assertTrue(turn.processed)
        self.assertSimilarTimestamp(turn.processed_at, datetime)
        self.assertEqual(1, len(models.TurnEnd.objects.all()))

    def test_process_standalone(self):
        turn = self.create_turn()
        datetime = timezone.now()
        process_turn(turn_id=turn.id, processed_at=datetime)
        turn.refresh_from_db()
        self.assertTrue(turn.processed)
        self.assertSimilarTimestamp(turn.processed_at, datetime)

    def test_turn_end_duplication(self):
        turn = self.create_turn()
        datetime = timezone.now()
        tomorrow = datetime + timezone.timedelta(days=1)

        models.TurnEnd.objects.new(turn=turn, datetime=datetime)

        with self.assertRaises(IntegrityError):
            models.TurnEnd.objects.new(turn=turn, datetime=tomorrow)

        # Assert that only one process_turn() task was invoked, not two.
        self.apply_async.assert_called_once_with(
            kwargs={'turn_id': turn.id, 'processed_at': datetime},
            eta=datetime,
        )

    def test_turn_end_graceful_fail(self):
        turn = self.create_turn()
        datetime = timezone.now()

        models.TurnEnd.objects.new(turn=turn, datetime=datetime)

        with patch(process_path) as process:
            process.side_effect = models.Turn.DoesNotExist
            process_turn(turn_id=turn.id, processed_at=datetime)
        self.assertEqual(0, len(models.TurnEnd.objects.all()))
