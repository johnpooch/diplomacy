import unittest
from adjudicator.order import Hold
from adjudicator.piece import Army
from adjudicator.territory import CoastalTerritory

from .base import AdjudicatorTestCaseMixin


class TestPiece(AdjudicatorTestCaseMixin, unittest.TestCase):

    def test_piece(self):

        london = CoastalTerritory(self.state, 1, 'London', 'England', [], [])
        wales = CoastalTerritory(self.state, 2, 'Wales', 'England', [], [])

        army = Army(self.state, 0, 'England', london)
        london_hold = Hold(self.state, 0, 'England', london)
        wales_hold = Hold(self.state, 0, 'England', wales)

        self.assertEqual(london_hold.piece, army)
        self.assertIsNone(wales_hold.piece)


class TestIsOrder(AdjudicatorTestCaseMixin, unittest.TestCase):

    def test_hold(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [], [])
        Army(self.state, 0, 'England', london)
        london_hold = Hold(self.state, 0, 'England', london)

        self.assertTrue(london_hold.is_hold)
        self.assertFalse(london_hold.is_move)
        with self.assertRaises(AttributeError):
            london_hold.is_fake_class_name
