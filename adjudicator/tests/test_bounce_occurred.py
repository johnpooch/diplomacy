import unittest

from adjudicator.order import Move
from adjudicator.piece import Army
from adjudicator.processor import process
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestBounceOccured(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

    def test_simple_bounce(self):
        pieces = [
            Army(0, Nations.FRANCE, self.territories.PICARDY),
            Army(0, Nations.GERMANY, self.territories.BURGUNDY),
        ]
        orders = [
            Move(0, Nations.FRANCE, self.territories.PICARDY, self.territories.PARIS),
            Move(0, Nations.GERMANY, self.territories.BURGUNDY, self.territories.PARIS),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)
        self.assertTrue(orders[0].target.bounce_occurred)

    def test_three_way_bounce(self):
        pieces = [
            Army(0, Nations.FRANCE, self.territories.PICARDY),
            Army(0, Nations.GERMANY, self.territories.BURGUNDY),
            Army(0, Nations.GERMANY, self.territories.GASCONY),
        ]
        orders = [
            Move(0, Nations.FRANCE, self.territories.PICARDY, self.territories.PARIS),
            Move(0, Nations.GERMANY, self.territories.BURGUNDY, self.territories.PARIS),
            Move(0, Nations.GERMANY, self.territories.GASCONY, self.territories.PARIS),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)
        self.assertTrue(orders[0].target.bounce_occurred)

    def test_no_contest(self):
        pieces = [
            Army(0, Nations.FRANCE, self.territories.PICARDY),
        ]
        orders = [
            Move(0, Nations.FRANCE, self.territories.PICARDY, self.territories.PARIS),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)
        self.assertFalse(orders[0].target.bounce_occurred)

    def test_no_attack(self):
        territory = self.territories.PARIS
        process(self.state)
        self.assertFalse(territory.bounce_occurred)
