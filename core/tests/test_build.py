from django.test import TestCase

from core import models
from core import factories
from core.models.base import OrderType, Phase, PieceType, Season


class TestBuild(TestCase):

    def setUp(self):
        self.variant = factories.VariantFactory()
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
        self.nation = models.Nation.objects.create(
            variant=self.variant,
            name='France',
        )
        self.nation_state = models.NationState.objects.create(
            nation=self.nation,
            turn=self.turn,
            user=self.user,
        )

    def test_only_build_and_disband_orders_are_available(self):
        self.assertEqual(
            self.turn.possible_order_types,
            [OrderType.BUILD, OrderType.DISBAND]
        )

    def test_unoccupied_territories(self):
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        territory_state = models.TerritoryState.objects.create(
            turn=self.turn,
            territory=territory,
            controlled_by=self.nation,
        )
        self.assertTrue(
            territory_state in
            self.nation_state.unoccupied_controlled_home_supply_centers.all()
        )
        piece = models.Piece.objects.create(
            game=self.game,
            nation=self.nation,
            type=PieceType.ARMY,
        )
        models.PieceState.objects.create(
            piece=piece,
            turn=self.turn,
            territory=territory,
        )
        self.assertFalse(
            territory_state in
            self.nation_state.unoccupied_controlled_home_supply_centers.all()
        )

    def test_delta_surplus(self):
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            turn=self.turn,
            territory=territory,
            controlled_by=self.nation
        )
        self.assertEqual(self.nation_state.supply_delta, 1)

    def test_delta_deficit(self):
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            turn=self.turn,
            territory=territory,
            controlled_by=None
        )
        piece = models.Piece.objects.create(
            game=self.game,
            nation=self.nation,
            type=PieceType.ARMY,
        )
        models.PieceState.objects.create(
            turn=self.turn,
            piece=piece,
            territory=territory,
        )
        self.assertEqual(self.nation_state.supply_delta, -1)

    def test_delta_even(self):
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            turn=self.turn,
            territory=territory,
            controlled_by=self.nation
        )
        piece = models.Piece.objects.create(
            game=self.game,
            nation=self.nation,
            type=PieceType.ARMY,
        )
        models.PieceState.objects.create(
            turn=self.turn,
            piece=piece,
            territory=territory,
        )
        self.assertEqual(self.nation_state.supply_delta, 0)

    def test_num_builds_surplus(self):
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            turn=self.turn,
            territory=territory,
            controlled_by=self.nation
        )
        self.assertEqual(self.nation_state.num_builds, 1)

    def test_num_builds_two_surplus(self):
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            turn=self.turn,
            territory=territory,
            controlled_by=self.nation
        )
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Marseilles',
            nationality=self.nation,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            turn=self.turn,
            territory=territory,
            controlled_by=self.nation
        )
        self.assertEqual(self.nation_state.num_builds, 2)

    def test_num_builds_two_surplus_one_blocked(self):
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            turn=self.turn,
            territory=territory,
            controlled_by=self.nation
        )
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Marseilles',
            nationality=self.nation,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            turn=self.turn,
            territory=territory,
            controlled_by=self.nation
        )
        piece = models.Piece.objects.create(
            game=self.game,
            nation=self.nation,
            type=PieceType.ARMY,
        )
        models.PieceState.objects.create(
            turn=self.turn,
            piece=piece,
            territory=territory,
        )
        self.assertEqual(self.nation_state.num_builds, 1)

    def test_num_builds_one_deficit(self):
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            turn=self.turn,
            territory=territory,
            controlled_by=None
        )
        piece = models.Piece.objects.create(
            game=self.game,
            nation=self.nation,
            type=PieceType.ARMY,
        )
        models.PieceState.objects.create(
            turn=self.turn,
            piece=piece,
            territory=territory,
        )
        self.assertEqual(self.nation_state.num_disbands, 1)
        self.assertEqual(self.nation_state.num_builds, 0)

    def test_build_creates_new_piece(self):
        pass

    def test_disband_removes_piece(self):
        pass
