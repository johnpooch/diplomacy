from django.test import TestCase

from core.models.base import OrderType, OutcomeType
from core.game import disband_pieces

from core.tests import DiplomacyTestCaseMixin


class TestDisbandPieces(TestCase, DiplomacyTestCaseMixin):

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(variant=self.variant)
        self.turn = self.create_test_turn(game=self.game, processed=True)
        self.england = self.variant.nations.create(name='England')
        self.france = self.variant.nations.create(name='France')
        self.london = self.create_test_territory(variant=self.variant, name='London')
        self.paris = self.create_test_territory(variant=self.variant, name='Paris')
        self.england_piece = self.create_test_piece(nation=self.england, game=self.game)
        self.france_piece = self.create_test_piece(nation=self.france, game=self.game)
        self.england_piece_state = self.create_test_piece_state(
            piece=self.england_piece,
            turn=self.turn,
            territory=self.london,
        )
        self.france_piece_state = self.create_test_piece_state(
            piece=self.france_piece,
            turn=self.turn,
            territory=self.paris,
        )

    def test_disband_pieces_no_orders(self):
        pieces = disband_pieces(self.turn)
        self.assertEqual(pieces, [])

    def test_disband_pieces_failing_order(self):
        self.turn.orders.create(
            source=self.london,
            outcome=OutcomeType.FAILS,
            nation=self.england,
            type=OrderType.DISBAND,
        )
        pieces = disband_pieces(self.turn)
        self.assertEqual(pieces, [])

    def test_disband_pieces_army(self):
        self.turn.orders.create(
            source=self.london,
            outcome=OutcomeType.SUCCEEDS,
            nation=self.england,
            type=OrderType.DISBAND,
        )
        pieces = disband_pieces(self.turn)
        self.assertEqual(len(pieces), 1)
        piece = pieces[0]
        self.assertEqual(piece, self.england_piece)
        self.assertEqual(piece.turn_disbanded, self.turn)

    def test_disband_retreat_correct_piece(self):
        self.turn.orders.create(
            source=self.london,
            outcome=OutcomeType.SUCCEEDS,
            nation=self.france,
            type=OrderType.DISBAND,
        )
        self.france_piece_state.territory = self.london
        self.france_piece_state.must_retreat = True
        self.france_piece_state.save()

        pieces = disband_pieces(self.turn)
        self.assertEqual(len(pieces), 1)
        piece = pieces[0]
        self.assertEqual(piece, self.france_piece)
        self.assertEqual(piece.turn_disbanded, self.turn)
