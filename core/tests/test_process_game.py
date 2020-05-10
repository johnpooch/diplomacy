from django.contrib.auth.models import User
from django.test import TestCase

from core import models
from core.models.base import GameStatus, OrderType, Phase, Season, TerritoryType


class TestProcessGame(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='Test User')
        self.variant = models.Variant.objects.create(name='standard')
        self.game = models.Game.objects.create(
            variant=self.variant,
            name='Test Game',
            description='Test Description',
            status=GameStatus.ACTIVE,
            num_players=7,
            created_by=self.user,
        )

    def test_basic_move(self):

        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.SPRING,
            phase=Phase.ORDER,
            year=1900,
        )
        france = models.Nation.objects.create(
            variant=self.variant,
            name='France',
        )
        paris = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=france,
            supply_center=True,
            type=TerritoryType.INLAND,
        )
        models.TerritoryState.objects.create(
            territory=paris,
            turn=turn,
            controlled_by=france,
        )
        picardy = models.Territory.objects.create(
            variant=self.variant,
            name='Picardy',
            nationality=france,
            type=TerritoryType.COASTAL,
        )
        models.TerritoryState.objects.create(
            territory=picardy,
            turn=turn,
            controlled_by=france,
        )
        army_paris = models.Piece.objects.create(
            game=self.game,
            nation=france,
        )
        models.PieceState.objects.create(
            piece=army_paris,
            turn=turn,
            territory=paris,
        )
        paris.neighbours.add(picardy)
        models.Order.objects.create(
            turn=turn,
            nation=france,
            type=OrderType.MOVE,
            source=paris,
            target=picardy,
        )
        self.game.process()
        new_turn = self.game.get_current_turn()
        self.assertEqual(new_turn.year, 1900)
        self.assertEqual(new_turn.phase, Phase.ORDER)
        self.assertEqual(new_turn.season, Season.FALL)
        piece_state = new_turn.piecestates.get()
        self.assertEqual(piece_state.territory, picardy)
