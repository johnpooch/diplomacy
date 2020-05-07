from django.contrib.auth.models import User
from django.test import TestCase

from core import models
from core import factories
from core.models.base import GameStatus, OutcomeType, OrderType, Phase, Season, TerritoryType


class TestGame(TestCase):

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

    def test_create_initial_turn(self):
        self.assertFalse(self.game.turns.all())
        with self.assertRaises(models.Turn.DoesNotExist):
            self.assertFalse(self.game.get_current_turn())
        self.game.create_initial_turn()
        current_turn = self.game.get_current_turn()
        self.assertEqual(current_turn.year, 1900)
        self.assertEqual(current_turn.season, Season.SPRING)
        self.assertEqual(current_turn.phase, Phase.ORDER)
        self.assertEqual(models.Turn.objects.count(), 1)

    def test_create_nation_states(self):
        turn = self.game.create_initial_turn()
        self.game.create_initial_nation_states()
        nation_states = turn.nationstates.all()
        self.assertEqual(len(nation_states), 7)
        for nation_state in nation_states:
            self.assertTrue(nation_state.user)

    def test_create_pieces(self):
        pass

    def test_create_piece_states(self):
        pass

    def test_randomly_assign_players(self):
        # random.shuffle
        pass

    def test_create_territory_states(self):
        pass
