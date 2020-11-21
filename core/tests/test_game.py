from django.test import TestCase

from core import factories, models
from core.models.base import GameStatus, Phase, Season
from core.tests import DiplomacyTestCaseMixin


class TestGame(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = models.Variant.objects.get(identifier='standard')
        self.users = []
        for i in range(7):
            self.users.append(factories.UserFactory())
        self.game = models.Game.objects.create(
            name='Test game',
            variant=self.variant,
            num_players=7,
            created_by=self.users[0],
        )
        self.game.participants.add(*self.users)

    def test_create_initial_turn(self):
        self.assertFalse(self.game.turns.all())
        with self.assertRaises(models.Turn.DoesNotExist):
            self.assertFalse(self.game.get_current_turn())
        self.game.create_initial_turn()
        current_turn = self.game.get_current_turn()
        self.assertEqual(current_turn.year, 1901)
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

    def test_create_territory_states(self):
        turn = self.game.create_initial_turn()
        self.game.create_initial_territory_states()
        territory_states = turn.territorystates.all()
        england = models.Nation.objects.get(variant=self.game.variant, name='England')
        london_state = turn.territorystates.get(territory__name='london')
        self.assertEqual(len(territory_states), 75)
        self.assertEqual(london_state.controlled_by, england)

    def test_create_pieces(self):
        turn = self.game.create_initial_turn()
        self.game.create_initial_pieces()
        pieces = self.game.pieces.all()
        self.assertEqual(len(pieces), 22)
        self.assertEqual(pieces.filter(nation__name='England').count(), 3)
        self.assertEqual(pieces.filter(nation__name='France').count(), 3)
        self.assertEqual(pieces.filter(nation__name='Italy').count(), 3)
        self.assertEqual(pieces.filter(nation__name='Austria-Hungary').count(), 3)
        self.assertEqual(pieces.filter(nation__name='Germany').count(), 3)
        self.assertEqual(pieces.filter(nation__name='Turkey').count(), 3)
        self.assertEqual(pieces.filter(nation__name='Russia').count(), 4)

        piece_states = turn.piecestates.all()
        self.assertEqual(len(piece_states), 22)
        self.assertEqual(piece_states.filter(piece__nation__name='England').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='France').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='Italy').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='Austria-Hungary').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='Germany').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='Turkey').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='Russia').count(), 4)

    def test_initialize(self):
        self.game.initialize()

        current_turn = self.game.get_current_turn()
        self.assertEqual(current_turn.year, 1901)
        self.assertEqual(current_turn.season, Season.SPRING)
        self.assertEqual(current_turn.phase, Phase.ORDER)
        self.assertEqual(models.Turn.objects.count(), 1)

        territory_states = current_turn.territorystates.all()
        england = models.Nation.objects.get(variant=self.game.variant, name='England')
        london_state = current_turn.territorystates.get(territory__name='london')
        self.assertEqual(len(territory_states), 75)
        self.assertEqual(london_state.controlled_by, england)

        pieces = self.game.pieces.all()
        self.assertEqual(len(pieces), 22)
        self.assertEqual(pieces.filter(nation__name='England').count(), 3)
        self.assertEqual(pieces.filter(nation__name='France').count(), 3)
        self.assertEqual(pieces.filter(nation__name='Italy').count(), 3)
        self.assertEqual(pieces.filter(nation__name='Austria-Hungary').count(), 3)
        self.assertEqual(pieces.filter(nation__name='Germany').count(), 3)
        self.assertEqual(pieces.filter(nation__name='Turkey').count(), 3)
        self.assertEqual(pieces.filter(nation__name='Russia').count(), 4)

        piece_states = current_turn.piecestates.all()
        self.assertEqual(len(piece_states), 22)
        self.assertEqual(piece_states.filter(piece__nation__name='England').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='France').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='Italy').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='Austria-Hungary').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='Germany').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='Turkey').count(), 3)
        self.assertEqual(piece_states.filter(piece__nation__name='Russia').count(), 4)

    def test_set_winners_one_winner(self):
        self.game.status = GameStatus.ACTIVE
        self.game.save()
        self.create_test_turn(game=self.game)
        france = self.variant.nations.get(name='France')
        self.game.set_winners(france)
        self.assertTrue(france in self.game.winners.all())
        self.assertEqual(self.game.status, GameStatus.ENDED)

    def test_set_winners_multiple_winners(self):
        self.game.status = GameStatus.ACTIVE
        self.game.save()
        self.create_test_turn(game=self.game)
        france = self.variant.nations.get(name='France')
        england = self.variant.nations.get(name='England')
        self.game.set_winners(france, england)
        self.assertTrue(france in self.game.winners.all())
        self.assertTrue(england in self.game.winners.all())
        self.assertEqual(self.game.status, GameStatus.ENDED)

    def test_invalid_nation(self):
        self.game.status = GameStatus.ACTIVE
        self.game.save()
        self.create_test_turn(game=self.game)
        france = self.variant.nations.get(name='France')
        other_variant = self.create_test_variant(name='Other')
        other_nation = self.create_test_nation(variant=other_variant)
        with self.assertRaises(ValueError):
            self.game.set_winners(france, other_nation)
        self.assertEqual(self.game.status, GameStatus.ACTIVE)
        self.assertEqual(self.game.winners.all().count(), 0)
