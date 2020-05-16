from django.test import TestCase

from core import models
from core import factories
from core.models.base import OrderType, Phase, PieceType, Season


class TestBuild(TestCase):

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
        self.turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.BUILD,
            season=Season.FALL,
            year=1901,
        )

    def test_only_build_and_disband_orders_are_available(self):
        self.assertEqual(
            self.retreat_turn.possible_order_types,
            [OrderType.RETREAT, OrderType.DISBAND]
        )

    def test_num_possible_builds_raises_on_non_build(self):
        pass

    def test_num_disbands_raises_on_non_build(self):
        pass

    def test_num_possible_builds(self):
        pass

    def test_num_disbands(self):
        pass

    def test_build_creates_new_piece(self):
        pass

    def test_disband_removes_piece(self):
        pass
