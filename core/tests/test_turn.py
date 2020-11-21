from django.test import TestCase

from core import factories, models
from core.models.base import PieceType, Phase, Season
from core.tests import DiplomacyTestCaseMixin


class TestTurn(DiplomacyTestCaseMixin, TestCase):

    def setUp(self):
        self.variant = models.Variant.objects.get(identifier='standard')
        self.user = factories.UserFactory()
        self.game = models.Game.objects.create(
            name='Test game',
            variant=self.variant,
            num_players=7,
            created_by=self.user,
        )
        self.game.participants.add(self.user)

    def test_ready_to_process_retreat(self):
        retreat_turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.RETREAT_AND_DISBAND,
            season=Season.FALL,
            year=1901,
        )
        england = self.variant.nations.get(name='England')
        france = self.variant.nations.get(name='France')
        other_user = factories.UserFactory()
        self.game.participants.add(other_user)
        models.NationState.objects.create(
            turn=retreat_turn,
            nation=england,
            user=other_user
        )
        france_state = models.NationState.objects.create(
            turn=retreat_turn,
            nation=france,
            user=self.user
        )
        piece = models.Piece.objects.create(
            game=self.game,
            nation=france,
            type=PieceType.ARMY,
        )
        models.PieceState.objects.create(
            piece=piece,
            turn=retreat_turn,
            must_retreat=True,
        )
        self.assertFalse(retreat_turn.ready_to_process)
        # only nation states which have orders to submit must finalize
        france_state.orders_finalized = True
        france_state.save()
        self.assertTrue(retreat_turn.ready_to_process)

    def test_ready_to_process_build(self):
        build_turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.BUILD,
            season=Season.FALL,
            year=1901,
        )
        england = self.variant.nations.get(name='England')
        france = self.variant.nations.get(name='France')
        other_user = factories.UserFactory()
        self.game.participants.add(other_user)
        models.NationState.objects.create(
            turn=build_turn,
            nation=england,
            user=other_user
        )
        france_state = models.NationState.objects.create(
            turn=build_turn,
            nation=france,
            user=self.user
        )
        territory = models.Territory.objects.create(
            variant=self.variant,
            name='Marseilles',
            nationality=france,
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            turn=build_turn,
            territory=territory,
            controlled_by=france,
        )
        self.assertFalse(build_turn.ready_to_process)
        # only nation states which have orders to submit must finalize
        france_state.orders_finalized = True
        france_state.save()
        self.assertTrue(build_turn.ready_to_process)

    def test_check_for_winning_nation(self):
        turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.ORDER,
            season=Season.FALL,
            year=1901,
        )
        france = self.variant.nations.get(name='France')
        france_state = models.NationState.objects.create(
            turn=turn,
            nation=france,
            user=self.user
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
        self.assertFalse(turn.check_for_winning_nation())
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
        self.assertTrue(turn.check_for_winning_nation())


class TestLinkedTurns(TestCase):

    def setUp(self):
        self.variant = factories.StandardVariantFactory()
        self.user = factories.UserFactory()
        self.game_a = models.Game.objects.create(
            name='Test game A',
            variant=self.variant,
            num_players=7,
            created_by=self.user,
        )
        self.game_b = models.Game.objects.create(
            name='Test game B',
            variant=self.variant,
            num_players=7,
            created_by=self.user,
        )
        self.game_a_spring_order_turn = models.Turn.objects.create(
            game=self.game_a,
            phase=Phase.ORDER,
            season=Season.SPRING,
            year=1901,
        )
        self.game_b_spring_order_turn = models.Turn.objects.create(
            game=self.game_b,
            phase=Phase.ORDER,
            season=Season.SPRING,
            year=1901,
        )
        self.game_a_spring_retreat_turn = models.Turn.objects.create(
            game=self.game_a,
            phase=Phase.RETREAT_AND_DISBAND,
            season=Season.SPRING,
            year=1901,
        )
        self.game_b_spring_retreat_turn = models.Turn.objects.create(
            game=self.game_b,
            phase=Phase.RETREAT_AND_DISBAND,
            season=Season.SPRING,
            year=1901,
        )
        self.game_a_fall_order_turn = models.Turn.objects.create(
            game=self.game_a,
            phase=Phase.ORDER,
            season=Season.FALL,
            year=1901,
        )
        self.game_b_fall_order_turn = models.Turn.objects.create(
            game=self.game_b,
            phase=Phase.ORDER,
            season=Season.FALL,
            year=1901,
        )
        self.game_a_fall_retreat_turn = models.Turn.objects.create(
            game=self.game_a,
            phase=Phase.RETREAT_AND_DISBAND,
            season=Season.FALL,
            year=1901,
        )
        self.game_b_fall_retreat_turn = models.Turn.objects.create(
            game=self.game_b,
            phase=Phase.RETREAT_AND_DISBAND,
            season=Season.FALL,
            year=1901,
        )
        self.game_a_fall_build_turn = models.Turn.objects.create(
            game=self.game_a,
            phase=Phase.BUILD,
            season=Season.FALL,
            year=1901,
        )
        self.game_b_fall_build_turn = models.Turn.objects.create(
            game=self.game_b,
            phase=Phase.BUILD,
            season=Season.FALL,
            year=1901,
        )
        self.game_a_spring_order_turn_1902 = models.Turn.objects.create(
            game=self.game_a,
            phase=Phase.ORDER,
            season=Season.SPRING,
            year=1902,
        )
        self.game_b_spring_order_turn_1902 = models.Turn.objects.create(
            game=self.game_b,
            phase=Phase.ORDER,
            season=Season.SPRING,
            year=1902,
        )

    def test_get_next_turn(self):
        turn = self.game_a_spring_order_turn
        turn = models.Turn.get_next(turn)
        self.assertEqual(turn, self.game_a_spring_retreat_turn)
        turn = models.Turn.get_next(turn)
        self.assertEqual(turn, self.game_a_fall_order_turn)
        turn = models.Turn.get_next(turn)
        self.assertEqual(turn, self.game_a_fall_retreat_turn)
        turn = models.Turn.get_next(turn)
        self.assertEqual(turn, self.game_a_fall_build_turn)
        turn = models.Turn.get_next(turn)
        self.assertEqual(turn, self.game_a_spring_order_turn_1902)
        turn = models.Turn.get_next(turn)
        self.assertIsNone(turn)

        turn = self.game_b_spring_order_turn
        turn = models.Turn.get_next(turn)
        self.assertEqual(turn, self.game_b_spring_retreat_turn)
        turn = models.Turn.get_next(turn)
        self.assertEqual(turn, self.game_b_fall_order_turn)
        turn = models.Turn.get_next(turn)
        self.assertEqual(turn, self.game_b_fall_retreat_turn)
        turn = models.Turn.get_next(turn)
        self.assertEqual(turn, self.game_b_fall_build_turn)
        turn = models.Turn.get_next(turn)
        self.assertEqual(turn, self.game_b_spring_order_turn_1902)
        turn = models.Turn.get_next(turn)
        self.assertIsNone(turn)

    def test_get_previous_turn(self):
        turn = self.game_a_spring_order_turn_1902
        turn = models.Turn.get_previous(turn)
        self.assertEqual(turn, self.game_a_fall_build_turn)
        turn = models.Turn.get_previous(turn)
        self.assertEqual(turn, self.game_a_fall_retreat_turn)
        turn = models.Turn.get_previous(turn)
        self.assertEqual(turn, self.game_a_fall_order_turn)
        turn = models.Turn.get_previous(turn)
        self.assertEqual(turn, self.game_a_spring_retreat_turn)
        turn = models.Turn.get_previous(turn)
        self.assertEqual(turn, self.game_a_spring_order_turn)
        turn = models.Turn.get_previous(turn)
        self.assertIsNone(turn)

        turn = self.game_b_spring_order_turn_1902
        turn = models.Turn.get_previous(turn)
        self.assertEqual(turn, self.game_b_fall_build_turn)
        turn = models.Turn.get_previous(turn)
        self.assertEqual(turn, self.game_b_fall_retreat_turn)
        turn = models.Turn.get_previous(turn)
        self.assertEqual(turn, self.game_b_fall_order_turn)
        turn = models.Turn.get_previous(turn)
        self.assertEqual(turn, self.game_b_spring_retreat_turn)
        turn = models.Turn.get_previous(turn)
        self.assertEqual(turn, self.game_b_spring_order_turn)
        turn = models.Turn.get_previous(turn)
        self.assertIsNone(turn)
