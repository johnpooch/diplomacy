import unittest
from core.adjudicator.order import Hold, Move
from core.adjudicator.piece import Piece, Army
from core.adjudicator.territory import CoastalTerritory


class PieceTestCase(unittest.TestCase):
    def setUp(self):
        Piece.all_orders = []


class TestOrder(PieceTestCase):

    def test_order_exists(self):
        london = CoastalTerritory(1, "London", "England", [], [])
        wales = CoastalTerritory(2, "Wales", "England", [], [])
        army = Army("England", london)
        london_move = Move("England", london, wales)

        self.assertEqual(army.order, london_move)

    def test_order_does_not_exist(self):
        pass
