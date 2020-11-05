from django.test import TestCase

from core import factories, models
from core.models.base import Phase, Season


class TestNation(TestCase):

    def setUp(self):
        self.variant = models.Variant.objects.create(
            name='Standard',
        )
        self.user = factories.UserFactory()
        self.game = models.Game.objects.create(
            name='Test game',
            variant=self.variant,
            num_players=7,
            created_by=self.user,
        )
        self.game.participants.add(self.user)

    def test_unoccupied_controlled_home_supply_centers(self):
        france = models.Nation.objects.create(
            variant=self.variant,
            name='France',
        )
        england = models.Nation.objects.create(
            variant=self.variant,
            name='England',
        )
        paris = models.Territory.objects.create(
            name='Paris',
            variant=self.variant,
            nationality=france,
            supply_center=True,
        )
        models.Territory.objects.create(
            name='London',
            variant=self.variant,
            nationality=france,
            supply_center=True,
        )
        holland = models.Territory.objects.create(
            name='Holland',
            variant=self.variant,
            nationality=None,
            supply_center=True,
        )
        order_turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.ORDER,
            season=Season.FALL,
            year=1901,
        )
        build_turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.BUILD,
            season=Season.FALL,
            year=1901,
        )
        france_piece = models.Piece.objects.create(
            game=self.game,
            nation=france,
        )
        france_build_state = models.NationState.objects.create(
            turn=build_turn,
            nation=france,
        )
        # unoccupied home controlled territory with supply center (occupied
        # previous turn)
        models.TerritoryState.objects.create(
            territory=paris,
            turn=order_turn,
            controlled_by=france,
        )
        paris_build_state = models.TerritoryState.objects.create(
            territory=paris,
            turn=build_turn,
            controlled_by=france,
        )
        models.PieceState.objects.create(
            turn=order_turn,
            piece=france_piece,
            territory=paris,
        )
        result = france_build_state.unoccupied_controlled_home_supply_centers
        self.assertTrue(paris_build_state in result)

        # unoccupied foreign controlled territory with supply center (occupied
        # previous turn)
        models.TerritoryState.objects.create(
            territory=holland,
            turn=order_turn,
            controlled_by=france,
        )
        holland_build_state = models.TerritoryState.objects.create(
            territory=holland,
            turn=build_turn,
            controlled_by=france,
        )
        models.PieceState.objects.create(
            turn=order_turn,
            piece=france_piece,
            territory=holland,
        )
        result = france_build_state.unoccupied_controlled_home_supply_centers
        self.assertFalse(holland_build_state in result)

        # occupied controlled territory with supply center
        models.TerritoryState.objects.create(
            territory=paris,
            turn=order_turn,
            controlled_by=france,
        )
        paris_build_state = models.TerritoryState.objects.create(
            territory=paris,
            turn=build_turn,
            controlled_by=france,
        )
        models.PieceState.objects.create(
            turn=build_turn,
            piece=france_piece,
            territory=paris,
        )
        result = france_build_state.unoccupied_controlled_home_supply_centers
        self.assertFalse(paris_build_state in result)
        # unoccupied controlled territory with no supply center
        paris.supply_center = False
        paris.save()
        models.TerritoryState.objects.create(
            territory=paris,
            turn=order_turn,
            controlled_by=france,
        )
        paris_build_state = models.TerritoryState.objects.create(
            territory=paris,
            turn=build_turn,
            controlled_by=france,
        )
        result = france_build_state.unoccupied_controlled_home_supply_centers
        self.assertFalse(paris_build_state in result)

        # unoccupied uncontrolled territory with supply center
        paris.supply_center = True
        paris.save()
        models.TerritoryState.objects.create(
            territory=paris,
            turn=order_turn,
            controlled_by=france,
        )
        paris_build_state = models.TerritoryState.objects.create(
            territory=paris,
            turn=build_turn,
            controlled_by=england,
        )
        result = france_build_state.unoccupied_controlled_home_supply_centers
        self.assertFalse(paris_build_state in result)

    def test_meets_victory_conditions(self):
        france = models.Nation.objects.create(
            variant=self.variant,
            name='France',
        )
        turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.ORDER,
            season=Season.FALL,
            year=1901,
        )
        france_state = models.NationState.objects.create(
            turn=turn,
            nation=france,
        )
        for i in range(17):
            territory = models.Territory.objects.create(
                name='Territory Name ' + str(i),
                variant=self.variant,
                nationality=france,
                supply_center=True,
            )
            models.TerritoryState.objects.create(
                territory=territory,
                turn=turn,
                controlled_by=france,
            )
        self.assertEqual(france_state.supply_centers.count(), 17)
        self.assertFalse(france_state.meets_victory_conditions)
        territory = models.Territory.objects.create(
            name='Winning territory',
            variant=self.variant,
            nationality=france,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            territory=territory,
            turn=turn,
            controlled_by=france,
        )
        self.assertEqual(france_state.supply_centers.count(), 18)
        self.assertTrue(france_state.meets_victory_conditions)
