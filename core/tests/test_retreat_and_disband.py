from django.test import TestCase

from core import models
from core import factories
from core.models.base import OrderType, Phase, PieceType, Season


class TestRetreatAndDisband(TestCase):

    def setUp(self):
        self.variant = factories.StandardVariantFactory()
        self.user = factories.UserFactory()
        self.game = models.Game.objects.create(
            name='Test game',
            variant=self.variant,
            num_players=7,
            created_by=self.user,
        )
        self.game.participants.add(self.user)
        self.retreat_turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.RETREAT_AND_DISBAND,
            season=Season.FALL,
            year=1901,
        )

    def test_only_retreat_and_disband_orders_are_available(self):
        self.assertEqual(
            self.retreat_turn.possible_order_types,
            [OrderType.RETREAT, OrderType.DISBAND]
        )

    def test_pieces_to_order_equal_to_num_pieces_which_must_retreat(self):
        france = self.variant.nations.get(name='France')
        nation_state = models.NationState.objects.create(
            turn=self.retreat_turn,
            nation=france,
            user=self.user
        )
        self.assertEqual(nation_state.pieces_to_order.count(), 0)
        piece = models.Piece.objects.create(
            game=self.game,
            nation=france,
            type=PieceType.ARMY,
        )
        piece_state = models.PieceState.objects.create(
            piece=piece,
            turn=self.retreat_turn,
        )
        self.assertEqual(nation_state.pieces_to_order.count(), 0)
        piece_state.must_retreat = True
        piece_state.save()
        self.assertEqual(nation_state.pieces_to_order.count(), 1)

    def test_pieces_which_are_disbanded_are_removed_from_the_game(self):
        pass

    def test_pieces_which_are_dislodged_must_retreat_next_turn(self):
        pass
