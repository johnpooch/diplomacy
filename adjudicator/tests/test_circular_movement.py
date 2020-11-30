import unittest

from adjudicator.order import Move
from adjudicator.piece import Army, Fleet
from adjudicator.paradoxes import find_circular_movements
from adjudicator.tests.data import NamedCoasts, Nations, Territories

from .base import AdjudicatorTestCaseMixin


class TestCircularMovement(AdjudicatorTestCaseMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.territories = Territories(self.state)
        self.named_coasts = NamedCoasts(self.state, self.territories)

    def test_head_to_head(self):

        Fleet(self.state, 0, Nations.TURKEY, self.territories.ANKARA),
        Army(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE),

        orders = [
            Move(self.state, 0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.ANKARA),
        ]
        result = find_circular_movements(orders)

        self.assertEqual(len(result), 0)

    def test_three_army_circular_movement(self):

        Fleet(self.state, 0, Nations.TURKEY, self.territories.ANKARA),
        Army(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
        Army(self.state, 0, Nations.TURKEY, self.territories.SMYRNA)

        orders = [
            Move(self.state, 0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(self.state, 0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA),
        ]
        result = find_circular_movements(orders)

        self.assertEqual(len(result), 1)
        self.assertTrue(all([o in result[0] for o in orders]))

    def test_four_army_circular_movement(self):

        Fleet(self.state, 0, Nations.TURKEY, self.territories.ANKARA),
        Army(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
        Army(self.state, 0, Nations.TURKEY, self.territories.SMYRNA),
        Army(self.state, 0, Nations.TURKEY, self.territories.ARMENIA)

        orders = [
            Move(self.state, 0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(self.state, 0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ARMENIA),
            Move(self.state, 0, Nations.TURKEY, self.territories.ARMENIA, self.territories.ANKARA),
        ]
        result = find_circular_movements(orders)

        self.assertEqual(len(result), 1)
        self.assertTrue(all([o in result[0] for o in orders]))

    def test_five_army_circular_movement(self):

        Fleet(self.state, 0, Nations.TURKEY, self.territories.ANKARA),
        Army(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
        Army(self.state, 0, Nations.TURKEY, self.territories.SMYRNA),
        Army(self.state, 0, Nations.TURKEY, self.territories.ARMENIA),
        Army(self.state, 0, Nations.TURKEY, self.territories.SYRIA),

        orders = [
            Move(self.state, 0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(self.state, 0, Nations.TURKEY, self.territories.SMYRNA, self.territories.SYRIA),
            Move(self.state, 0, Nations.TURKEY, self.territories.SYRIA, self.territories.ARMENIA),
            Move(self.state, 0, Nations.TURKEY, self.territories.ARMENIA, self.territories.ANKARA),
        ]
        result = find_circular_movements(orders)

        self.assertEqual(len(result), 1)
        self.assertTrue(all([o in result[0] for o in orders]))

    def test_two_separate_circular_movements(self):
        Fleet(self.state, 0, Nations.TURKEY, self.territories.ANKARA),
        Army(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE),
        Army(self.state, 0, Nations.TURKEY, self.territories.SMYRNA),

        Army(self.state, 0, Nations.FRANCE, self.territories.BREST),
        Army(self.state, 0, Nations.FRANCE, self.territories.PICARDY),
        Army(self.state, 0, Nations.FRANCE, self.territories.PARIS),

        orders = [
            Move(self.state, 0, Nations.TURKEY, self.territories.ANKARA, self.territories.CONSTANTINOPLE),
            Move(self.state, 0, Nations.TURKEY, self.territories.CONSTANTINOPLE, self.territories.SMYRNA),
            Move(self.state, 0, Nations.TURKEY, self.territories.SMYRNA, self.territories.ANKARA),

            Move(self.state, 0, Nations.FRANCE, self.territories.BREST, self.territories.PICARDY),
            Move(self.state, 0, Nations.FRANCE, self.territories.PICARDY, self.territories.PARIS),
            Move(self.state, 0, Nations.FRANCE, self.territories.PARIS, self.territories.BREST),
        ]
        result = find_circular_movements(orders)

        self.assertEqual(len(result), 2)
        self.assertTrue(all([o in result[0] for o in orders[:3]]))
        self.assertTrue(all([o in result[1] for o in orders[3:]]))

    def test_empty_input(self):
        orders = []
        result = find_circular_movements(orders)
        self.assertEqual(len(result), 0)
