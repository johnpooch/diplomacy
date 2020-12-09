from django.test import TestCase

from core.models.base import OrderType, OutcomeType, PieceType
from core.game import create_new_pieces

from core.tests import DiplomacyTestCaseMixin


class TestCreateNewPieces(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(variant=self.variant)
        self.turn = self.create_test_turn(game=self.game, processed=True)
        self.england = self.variant.nations.create(name='England')
        self.france = self.variant.nations.create(name='France')
        self.london = self.create_test_territory(variant=self.variant, name='London')
        self.paris = self.create_test_territory(variant=self.variant, name='Paris')

    def test_create_new_pieces_no_orders(self):
        pieces = create_new_pieces(self.turn)
        self.assertEqual(pieces, [])

    def test_create_new_pieces_failing_order(self):
        self.turn.orders.create(
            source=self.london,
            outcome=OutcomeType.FAILS,
            nation=self.england,
            type=OrderType.BUILD,
            piece_type=PieceType.ARMY,
        )
        pieces = create_new_pieces(self.turn)
        self.assertEqual(pieces, [])

    def test_create_new_pieces_army(self):
        self.turn.orders.create(
            source=self.london,
            outcome=OutcomeType.SUCCEEDS,
            nation=self.england,
            type=OrderType.BUILD,
            piece_type=PieceType.ARMY,
        )
        pieces = create_new_pieces(self.turn)
        self.assertEqual(len(pieces), 1)
        piece = pieces[0]
        self.assertEqual(piece.nation, self.england)
        self.assertEqual(piece.game, self.game)
        self.assertEqual(piece.type, PieceType.ARMY)

    def test_create_new_fleet(self):
        self.turn.orders.create(
            source=self.london,
            outcome=OutcomeType.SUCCEEDS,
            nation=self.england,
            type=OrderType.BUILD,
            piece_type=PieceType.FLEET,
        )
        piece = create_new_pieces(self.turn)[0]
        self.assertEqual(piece.type, PieceType.FLEET)

    def test_create_both_types_different_nations(self):
        self.turn.orders.create(
            source=self.london,
            outcome=OutcomeType.SUCCEEDS,
            nation=self.england,
            type=OrderType.BUILD,
            piece_type=PieceType.ARMY,
        )
        self.turn.orders.create(
            source=self.paris,
            outcome=OutcomeType.SUCCEEDS,
            nation=self.france,
            type=OrderType.BUILD,
            piece_type=PieceType.FLEET,
        )
        pieces = create_new_pieces(self.turn)
        self.assertEqual(len(pieces), 2)

    def test_create_both_types_same_nation(self):
        self.turn.orders.create(
            source=self.london,
            outcome=OutcomeType.SUCCEEDS,
            nation=self.england,
            type=OrderType.BUILD,
            piece_type=PieceType.ARMY,
        )
        self.turn.orders.create(
            source=self.paris,
            outcome=OutcomeType.SUCCEEDS,
            nation=self.england,
            type=OrderType.BUILD,
            piece_type=PieceType.FLEET,
        )
        pieces = create_new_pieces(self.turn)
        self.assertEqual(len(pieces), 2)
