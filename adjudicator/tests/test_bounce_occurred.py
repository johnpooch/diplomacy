import unittest

from adjudicator.order import Move
from adjudicator.piece import Army
from adjudicator.processor import process
from adjudicator.tests.data import NamedCoasts, Nations, Territories

from .base import AdjudicatorTestCaseMixin


class TestBounceOccured(AdjudicatorTestCaseMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.territories = Territories(self.state)
        self.named_coasts = NamedCoasts(self.state, self.territories)

    def test_simple_bounce(self):
        Army(self.state, 0, Nations.FRANCE, self.territories.PICARDY),
        Army(self.state, 0, Nations.GERMANY, self.territories.BURGUNDY),
        orders = [
            Move(self.state, 0, Nations.FRANCE, self.territories.PICARDY, self.territories.PARIS),
            Move(self.state, 0, Nations.GERMANY, self.territories.BURGUNDY, self.territories.PARIS),
        ]
        process(self.state)
        self.assertTrue(orders[0].target.bounce_occurred)

    def test_three_way_bounce(self):
        Army(self.state, 0, Nations.FRANCE, self.territories.PICARDY),
        Army(self.state, 0, Nations.GERMANY, self.territories.BURGUNDY),
        Army(self.state, 0, Nations.GERMANY, self.territories.GASCONY),
        orders = [
            Move(self.state, 0, Nations.FRANCE, self.territories.PICARDY, self.territories.PARIS),
            Move(self.state, 0, Nations.GERMANY, self.territories.BURGUNDY, self.territories.PARIS),
            Move(self.state, 0, Nations.GERMANY, self.territories.GASCONY, self.territories.PARIS),
        ]
        process(self.state)
        self.assertTrue(orders[0].target.bounce_occurred)

    def test_no_contest(self):
        Army(self.state, 0, Nations.FRANCE, self.territories.PICARDY),
        orders = [
            Move(self.state, 0, Nations.FRANCE, self.territories.PICARDY, self.territories.PARIS),
        ]
        process(self.state)
        self.assertFalse(orders[0].target.bounce_occurred)

    def test_no_attack(self):
        territory = self.territories.PARIS
        process(self.state)
        self.assertFalse(territory.bounce_occurred)
