from django.test import TestCase

from service.models import Command, Game, Nation, Order, Phase, Piece, \
        Territory, Turn


class InitialGameStateTestCase(TestCase):
    """
    """
    def setUp(self):
        # Game State
        self.game = Game.objects.create(
            name='test game',
        )
        self.phase = Phase.objects.create(
            season='S',
            type='O',
        )
        self.turn = Turn.objects.create(
            year=1900,
            phase=self.phase,
            game=self.game,
            current_turn=True,
        )
