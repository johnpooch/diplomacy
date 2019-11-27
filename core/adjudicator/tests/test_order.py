import unittest
from core.adjudicator.order import Hold, Order
from core.adjudicator.piece import Army
from core.adjudicator.territory import CoastalTerritory


class OrderTestCase(unittest.TestCase):
    def setUp(self):
        Order.all_territories = []


class TestPiece(OrderTestCase):

    def test_piece(self):
        london = CoastalTerritory(1, "London", "England", [], [])
        wales = CoastalTerritory(2, "Wales", "England", [], [])

        army = Army("England", london)
        London_hold = Hold("England", london)
        Wales_hold = Hold("England", wales)

        self.assertEqual(London_hold.piece, army)
        self.assertIsNone(Wales_hold.piece)
