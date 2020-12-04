from django.test import TestCase

from core.models.base import OrderType, OutcomeType, Season
from core.tests import DiplomacyTestCaseMixin


class TestPieceState(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(variant=self.variant)
        self.england = self.variant.nations.create(name='England')
        self.territory = self.create_test_territory(variant=self.variant)
        self.other_territory = self.create_test_territory(variant=self.variant, name='Other')
        self.named_coast = self.create_test_named_coast(parent=self.other_territory)
        self.turn = self.create_test_turn(game=self.game)
        self.new_turn = self.create_test_turn(game=self.game, season=Season.FALL)
        self.user = self.create_test_user()

        self.piece = self.create_test_piece(
            game=self.game,
            nation=self.england,
        )
        self.piece_state = self.create_test_piece_state(
            piece=self.piece,
            turn=self.turn,
            territory=self.territory,
        )

    def test_unsuccessful_move_order(self):
        self.create_test_order(
            turn=self.turn,
            type=OrderType.MOVE,
            source=self.territory,
            nation=self.england,
        )
        self.assertIsNone(self.piece_state.successful_move_order)

    def test_unsuccessful_retreat_order(self):
        self.create_test_order(
            turn=self.turn,
            type=OrderType.RETREAT,
            source=self.territory,
            nation=self.england,
        )
        self.assertIsNone(self.piece_state.successful_move_order)

    def test_successful_move_order(self):
        order = self.create_test_order(
            turn=self.turn,
            type=OrderType.MOVE,
            source=self.territory,
            nation=self.england,
            outcome=OutcomeType.SUCCEEDS,
        )
        self.assertEqual(self.piece_state.successful_move_order, order)

    def test_successful_retreat_order(self):
        order = self.create_test_order(
            turn=self.turn,
            type=OrderType.RETREAT,
            source=self.territory,
            nation=self.england,
            outcome=OutcomeType.SUCCEEDS,
        )
        self.assertEqual(self.piece_state.successful_move_order, order)

    def test_successful_support_order(self):
        self.create_test_order(
            turn=self.turn,
            type=OrderType.SUPPORT,
            source=self.territory,
            nation=self.england,
            outcome=OutcomeType.SUCCEEDS,
        )
        self.assertIsNone(self.piece_state.successful_move_order)

    def test_copy_to_new_turn_disbanded(self):
        self.piece.turn_disbanded = self.turn
        self.piece.save()
        self.assertIsNone(self.piece_state.copy_to_new_turn(self.new_turn))

    def test_copy_successful_move_order(self):
        order = self.create_test_order(
            turn=self.turn,
            type=OrderType.MOVE,
            source=self.territory,
            target=self.other_territory,
            target_coast=self.named_coast,
            nation=self.england,
            outcome=OutcomeType.SUCCEEDS,
        )
        new_piece_state = self.piece_state.copy_to_new_turn(self.new_turn)
        self.assertEqual(new_piece_state.territory, order.target)
        self.assertEqual(new_piece_state.named_coast, order.target_coast)

    def test_copy_successful_retreat_order(self):
        order = self.create_test_order(
            turn=self.turn,
            type=OrderType.RETREAT,
            source=self.territory,
            target=self.other_territory,
            target_coast=self.named_coast,
            nation=self.england,
            outcome=OutcomeType.SUCCEEDS,
        )
        new_piece_state = self.piece_state.copy_to_new_turn(self.new_turn)
        self.assertEqual(new_piece_state.territory, order.target)
        self.assertEqual(new_piece_state.named_coast, order.target_coast)

    def test_copy_dislodged(self):
        self.piece_state.dislodged = True
        new_piece_state = self.piece_state.copy_to_new_turn(self.new_turn)
        self.assertFalse(new_piece_state.dislodged)
        self.assertTrue(new_piece_state.must_retreat)
