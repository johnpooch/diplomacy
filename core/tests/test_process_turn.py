from django.contrib.auth.models import User
from django.test import TestCase

from core import models
from core.models.base import GameStatus, OutcomeType, OrderType, Phase, \
    Season, TerritoryType


class TestProcessTurn(TestCase):

    def test_process_turn(self):
        user = User.objects.create(username='Test User')
        variant = models.Variant.objects.create(name='standard')
        game = models.Game.objects.create(
            variant=variant,
            name='Test Game',
            description='Test Description',
            status=GameStatus.ACTIVE,
            num_players=7,
            created_by=user,
        )
        turn = models.Turn.objects.create(
            game=game,
            season=Season.SPRING,
            phase=Phase.ORDER,
            year=1900,
        )
        france = models.Nation.objects.create(
            variant=variant,
            name='France',
        )
        paris = models.Territory.objects.create(
            variant=variant,
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
            variant=variant,
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
            game=game,
            nation=france,
        )
        models.PieceState.objects.create(
            piece=army_paris,
            turn=turn,
            territory=paris,
        )
        paris.neighbours.add(picardy)
        order = models.Order.objects.create(
            turn=turn,
            nation=france,
            type=OrderType.MOVE,
            source=paris,
            target=picardy,
        )
        game_state_dict = turn._to_game_state_dict()
        expected_keys = ['orders', 'territories', 'named_coasts', 'pieces', 'phase', 'variant']
        self.assertTrue(all([e in game_state_dict.keys() for e in expected_keys]))
        self.assertEqual(len(game_state_dict['territories']), 2)
        self.assertEqual(len(game_state_dict['pieces']), 1)
        self.assertEqual(len(game_state_dict['named_coasts']), 0)
        self.assertEqual(game_state_dict['variant'], 'standard')

        turn.process()
        turn.refresh_from_db()
        self.assertTrue(turn.processed)
        order.refresh_from_db()
        self.assertEqual(order.outcome, OutcomeType.MOVES)

    def test_bounce_occured(self):
        user = User.objects.create(username='Test User')
        variant = models.Variant.objects.create(name='standard')
        game = models.Game.objects.create(
            variant=variant,
            name='Test Game',
            description='Test Description',
            status=GameStatus.ACTIVE,
            num_players=7,
            created_by=user,
        )
        turn = models.Turn.objects.create(
            game=game,
            season=Season.SPRING,
            phase=Phase.ORDER,
            year=1900,
        )
        france = models.Nation.objects.create(
            variant=variant,
            name='France',
        )
        paris = models.Territory.objects.create(
            variant=variant,
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
            variant=variant,
            name='Picardy',
            nationality=france,
            supply_center=False,
            type=TerritoryType.COASTAL,
        )
        models.TerritoryState.objects.create(
            territory=picardy,
            turn=turn,
            controlled_by=france,
        )
        burgundy = models.Territory.objects.create(
            variant=variant,
            name='Burgundy',
            nationality=france,
            supply_center=False,
            type=TerritoryType.COASTAL,
        )
        burgundy_state = models.TerritoryState.objects.create(
            territory=burgundy,
            turn=turn,
            controlled_by=france,
        )
        army_paris = models.Piece.objects.create(
            game=game,
            nation=france,
        )
        models.PieceState.objects.create(
            piece=army_paris,
            turn=turn,
            territory=paris,
        )
        army_picardy = models.Piece.objects.create(
            game=game,
            nation=france,
        )
        models.PieceState.objects.create(
            piece=army_picardy,
            turn=turn,
            territory=picardy,
        )
        paris_order = models.Order.objects.create(
            turn=turn,
            nation=france,
            type=OrderType.MOVE,
            source=paris,
            target=burgundy,
        )
        picardy_order = models.Order.objects.create(
            turn=turn,
            nation=france,
            type=OrderType.MOVE,
            source=paris,
            target=burgundy,
        )
        game.process()
        turn.refresh_from_db()
        burgundy_state.refresh_from_db()
        paris_order.refresh_from_db()
        picardy_order.refresh_from_db()
        self.assertTrue(turn.processed)
        self.assertTrue(burgundy_state.bounce_occurred)
        self.assertEqual(paris_order.outcome, OutcomeType.FAILS)
        self.assertEqual(picardy_order.outcome, OutcomeType.FAILS)

        new_turn = game.get_current_turn()
        new_burgundy_state = new_turn.territorystates.get(
            territory__name=burgundy_state.territory.name
        )
        self.assertEqual(new_burgundy_state.contested, True)
