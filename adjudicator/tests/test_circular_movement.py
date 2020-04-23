import unittest

from adjudicator.order import Move
from adjudicator.piece import Army, Fleet
from adjudicator.paradoxes import find_circular_movements
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestCircularMovement(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

    def test_head_to_head(self):
        pieces = [
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
            Army(0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
        ]
        orders = [
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.ANKARA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        result = find_circular_movements(orders)

        self.assertEqual(len(result), 0)

    def test_three_army_circular_movement(self):
        pieces = [
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
            Army(0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
            Army(0, Nations.TURKEY, self.territories.SMYRNA)
        ]
        orders = [
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        result = find_circular_movements(orders)

        self.assertEqual(len(result), 1)
        self.assertTrue(all([o in result[0] for o in orders]))

    def test_four_army_circular_movement(self):
        pieces = [
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
            Army(0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
            Army(0, Nations.TURKEY, self.territories.SMYRNA),
            Army(0, Nations.TURKEY, self.territories.ARMENIA)
        ]
        orders = [
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ARMENIA),
            Move(0, Nations.TURKEY, self.territories.ARMENIA, self.territories.ANKARA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        result = find_circular_movements(orders)

        self.assertEqual(len(result), 1)
        self.assertTrue(all([o in result[0] for o in orders]))

    def test_five_army_circular_movement(self):
        pieces = [
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
            Army(0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
            Army(0, Nations.TURKEY, self.territories.SMYRNA),
            Army(0, Nations.TURKEY, self.territories.ARMENIA),
            Army(0, Nations.TURKEY, self.territories.SYRIA),
        ]
        orders = [
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(0, Nations.TURKEY, self.territories.SMYRNA, self.territories.SYRIA),
            Move(0, Nations.TURKEY, self.territories.SYRIA, self.territories.ARMENIA),
            Move(0, Nations.TURKEY, self.territories.ARMENIA, self.territories.ANKARA),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        result = find_circular_movements(orders)

        self.assertEqual(len(result), 1)
        self.assertTrue(all([o in result[0] for o in orders]))

    def test_two_separate_circular_movements(self):
        pieces = [
            Fleet(0, Nations.TURKEY, self.territories.ANKARA),
            Army(0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
            Army(0, Nations.TURKEY, self.territories.SMYRNA),

            Army(0, Nations.FRANCE, self.territories.BREST),
            Army(0, Nations.FRANCE, self.territories.PICARDY),
            Army(0, Nations.FRANCE, self.territories.PARIS),
        ]
        orders = [
            Move(0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA),

            Move(0, Nations.FRANCE, self.territories.BREST, self.territories.PICARDY),
            Move(0, Nations.FRANCE, self.territories.PICARDY, self.territories.PARIS),
            Move(0, Nations.FRANCE, self.territories.PARIS, self.territories.BREST),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        result = find_circular_movements(orders)

        self.assertEqual(len(result), 2)
        self.assertTrue(all([o in result[0] for o in orders[:3]]))
        self.assertTrue(all([o in result[1] for o in orders[3:]]))

    def test_empty_input(self):
        orders = []
        result = find_circular_movements(orders)
        self.assertEqual(len(result), 0)

