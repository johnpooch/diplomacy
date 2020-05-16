from django.test import TestCase

from core import models
from core import factories
from core.models.base import OrderType, Phase, Season


class TestRetreatAndDisband(TestCase):

    def setUp(self):
        variant = factories.StandardVariantFactory()
        user = factories.UserFactory()
        self.game = models.Game.objects.create(
            name='Test game',
            variant=variant,
            num_players=7,
            created_by=user,
        )
        self.game.participants.add(user)
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
        pass

    def test_pieces_which_are_disbanded_are_removed_from_the_game(self):
        pass

    def test_pieces_which_are_dislodged_must_retreat_next_turn(self):
        pass
