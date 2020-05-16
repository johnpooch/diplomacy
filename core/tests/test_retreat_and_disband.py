from django.test import TestCase

from core import models
from core import factories
from core.models.base import Phase, Season


class TestRetreatAndDisband(TestCase):

    def setUp(self):
        variant = factories.StandardVariantFactory()
        users = []
        for i in range(7):
            users.append(factories.UserFactory())
        self.game = models.Game.objects.create(
            name='Test game',
            variant=variant,
            num_players=7,
            created_by=users[0],
        )
        self.game.participants.add(*users)

    def test_only_retreat_and_disband_orders_are_available(self):
        pass

    def test_pieces_to_order_equal_to_num_pieces_which_must_retreat(self):
        pass

    def test_pieces_which_are_disbanded_are_removed_from_the_game(self):
        pass

    def test_pieces_which_are_dislodged_must_retreat_next_turn(self):
        pass
