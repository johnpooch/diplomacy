"""
Add games to the DATA_DIR using the `dump_turn` management command.
"""

from django.test import TestCase

from core import models
from core.game import process_turn
from core.models.base import Phase, Season


DATA_DIR = 'tests/turn_1/'


class TestProcessTurn1(TestCase):

    fixtures = [
        DATA_DIR + '/created_by.json',
        DATA_DIR + '/participants.json',
        DATA_DIR + '/game.json',
        DATA_DIR + '/turn.json',
        DATA_DIR + '/nation_state.json',
        DATA_DIR + '/territory_state.json',
        DATA_DIR + '/piece.json',
        DATA_DIR + '/piece_state.json',
        DATA_DIR + '/order.json',
    ]

    def setUp(self):
        self.turn = models.Turn.objects.get()

    def test_processed(self):
        new_turn = process_turn(self.turn)

        # Test turn
        self.assertEqual(new_turn.season, Season.FALL)
        self.assertEqual(new_turn.phase, Phase.ORDER)
        self.assertEqual(new_turn.year, 1901)
        self.assertEqual(new_turn.processed, False)
        self.assertEqual(new_turn.processed_at, None)
        self.assertEqual(new_turn.current_turn, True)

        # Test nation states
        for nation_state in new_turn.nationstates.all():
            old_nation_state = self.turn.nationstates.get(nation=nation_state.nation)
            # All users have been copied over correctly
            self.assertEqual(nation_state.user, old_nation_state.user)
            # orders_finailzed set to False
            self.assertFalse(nation_state.orders_finalized)
