from unittest.mock import patch

from django.test import TestCase

from core import factories, models
from core.models.base import PieceType, Phase, Season, SurrenderStatus
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

    def test_toggle_no_current_turn(self):
        turn = self.create_test_turn(game=self.game, current_turn=False)
        user = self.create_test_user()
        with self.assertRaises(ValueError):
            turn.toggle_surrender(user)

    @patch('core.models.Turn.cancel_surrender')
    def test_toggle_surrender_surrendering(self, patch_cancel):
        turn = self.create_test_turn(game=self.game)
        user = self.create_test_user()
        models.Surrender.objects.create(user=user, turn=turn)
        turn.toggle_surrender(user)
        patch_cancel.assert_called()

    @patch('core.models.Turn.surrender_user')
    def test_toggle_surrender_not_surrendering(self, patch_surrender):
        turn = self.create_test_turn(game=self.game)
        user = self.create_test_user()
        turn.toggle_surrender(user)
        patch_surrender.assert_called()

    def test_surrender_user_no_current_turn(self):
        turn = self.create_test_turn(game=self.game, current_turn=False)
        user = self.create_test_user()
        with self.assertRaises(ValueError):
            turn.surrender_user(user)

    def test_surrender_user_user_not_controlling(self):
        turn = self.create_test_turn(game=self.game)
        user = self.create_test_user()
        with self.assertRaises(models.NationState.DoesNotExist):
            turn.surrender_user(user)

    def test_surrender_user_user_already_surrendering(self):
        turn = self.create_test_turn(game=self.game)
        user = self.create_test_user()
        self.create_test_nation_state(user=user, turn=turn)
        models.Surrender.objects.create(user=user, turn=turn)
        with self.assertRaises(ValueError):
            turn.surrender_user(user)

    def test_surrender_user(self):
        turn = self.create_test_turn(game=self.game)
        user = self.create_test_user()
        nation_state = self.create_test_nation_state(user=user, turn=turn)
        self.create_test_order(
            nation=nation_state.nation,
            turn=turn,
        )
        surrender = turn.surrender_user(user)
        self.assertEqual(surrender.turn, turn)
        self.assertEqual(surrender.user, user)
        self.assertEqual(surrender.status, SurrenderStatus.PENDING)
        self.assertTrue(surrender.created_at)
        self.assertEqual(models.Order.objects.count(), 0)

    def test_cancel_surrender_no_current_turn(self):
        turn = self.create_test_turn(game=self.game, current_turn=False)
        user = self.create_test_user()
        with self.assertRaises(ValueError):
            turn.cancel_surrender(user)

    def test_cancel_surrender_not_surrendering(self):
        turn = self.create_test_turn(game=self.game)
        user = self.create_test_user()
        self.create_test_nation_state(user=user, turn=turn)
        with self.assertRaises(models.Surrender.DoesNotExist):
            turn.cancel_surrender(user)

    def test_cancel_surrender(self):
        turn = self.create_test_turn(game=self.game)
        user = self.create_test_user()
        self.create_test_nation_state(user=user, turn=turn)
        models.Surrender.objects.create(user=user, turn=turn)
        surrender = turn.cancel_surrender(user)
        self.assertEqual(surrender.status, SurrenderStatus.CANCELED)
        self.assertTrue(surrender.resolved_at)

    def test_replace_surrendering_no_current_turn(self):
        turn = self.create_test_turn(game=self.game, current_turn=False)
        surrendering_user = self.create_test_user()
        new_user = self.create_test_user()
        with self.assertRaises(ValueError):
            turn.replace_surrendering_user(surrendering_user, new_user)

    def test_replace_surrendering_surrending_user_not_controlling_nation(self):
        turn = self.create_test_turn(game=self.game)
        surrendering_user = self.create_test_user()
        new_user = self.create_test_user()
        with self.assertRaises(models.NationState.DoesNotExist):
            turn.replace_surrendering_user(surrendering_user, new_user)

    def test_replace_surrendering_new_user_already_participating(self):
        turn = self.create_test_turn(game=self.game)
        surrendering_user = self.create_test_user()
        self.create_test_nation_state(user=surrendering_user, turn=turn)
        models.Surrender.objects.create(user=surrendering_user, turn=turn)
        new_user = self.create_test_user()
        self.game.participants.add(new_user)
        with self.assertRaises(ValueError):
            turn.replace_surrendering_user(surrendering_user, new_user)

    def test_replace_surrendering_surrending_user_not_surrendering(self):
        turn = self.create_test_turn(game=self.game)
        surrendering_user = self.create_test_user()
        self.create_test_nation_state(user=surrendering_user, turn=turn)
        new_user = self.create_test_user()
        self.game.participants.add(new_user)
        with self.assertRaises(models.Surrender.DoesNotExist):
            turn.replace_surrendering_user(surrendering_user, new_user)

    def test_replace_surrendering_user(self):
        turn = self.create_test_turn(game=self.game)
        surrendering_user = self.create_test_user()
        self.create_test_nation_state(
            user=surrendering_user,
            turn=turn
        )
        models.Surrender.objects.create(
            user=surrendering_user,
            turn=turn
        )
        new_user = self.create_test_user()
        surrender, nation_state = turn.replace_surrendering_user(
            surrendering_user,
            new_user
        )
        self.assertEqual(nation_state.user, new_user)
        self.assertEqual(surrender.replaced_by, new_user)
        self.assertTrue(surrender.resolved_at)
        self.assertEqual(surrender.status, SurrenderStatus.FULFILLED)
        self.assertTrue(new_user in self.game.participants.all())


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
