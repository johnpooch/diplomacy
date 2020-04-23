import unittest
from adjudicator.order import Hold
from adjudicator.piece import Army
from adjudicator.state import State
from adjudicator.territory import CoastalTerritory


class TestPiece(unittest.TestCase):

    def test_piece(self):
        state = State()

        london = CoastalTerritory(1, 'London', 'England', [], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [], [])

        army = Army(0, 'England', london)
        london_hold = Hold(0, 'England', london)
        wales_hold = Hold(0, 'England', wales)

        to_register = [london, wales, army, london_hold, wales_hold]
        [state.register(o) for o in to_register]

        self.assertEqual(london_hold.piece, army)
        self.assertIsNone(wales_hold.piece)


class TestIsOrder(unittest.TestCase):

    def test_hold(self):
        london = CoastalTerritory(1, 'London', 'England', [], [])
        Army(0, 'England', london)
        london_hold = Hold(0, 'England', london)

        self.assertTrue(london_hold.is_hold)
        self.assertFalse(london_hold.is_move)
        with self.assertRaises(AttributeError):
            london_hold.is_fake_class_name
