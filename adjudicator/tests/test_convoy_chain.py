import unittest

from adjudicator.order import Convoy
from adjudicator.convoy_chain import get_convoy_chains
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestConvoyChain(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

    def test_one_fleet_chain(self):
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.BREST, self.territories.LONDON),
        ]
        source = self.territories.BREST
        target = self.territories.LONDON
        result = get_convoy_chains(source, target, orders)
        self.assertEqual(result[0].convoys, [orders[0]])

    def test_two_fleet_chain(self):
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.MID_ATLANTIC, self.territories.PORTUGAL, self.territories.LONDON),
            Convoy(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.PORTUGAL, self.territories.LONDON),
        ]
        source = self.territories.PORTUGAL
        target = self.territories.LONDON
        result = get_convoy_chains(source, target, orders)

        self.assertTrue(all([o in result[0].convoys for o in orders]))
        self.assertEqual(len(result[0].convoys), 2)
        self.assertEqual(len(result), 1)

    def test_three_fleet_chain(self):
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.MID_ATLANTIC, self.territories.PORTUGAL, self.territories.NORWAY),
            Convoy(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.PORTUGAL, self.territories.NORWAY),
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.PORTUGAL, self.territories.NORWAY),
        ]
        source = self.territories.PORTUGAL
        target = self.territories.NORWAY
        result = get_convoy_chains(source, target, orders)
        self.assertTrue(all([o in result[0].convoys for o in orders]))
        self.assertEqual(len(result[0].convoys), 3)
        self.assertEqual(len(result), 1)

    def test_two_one_fleet_chains(self):
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.BELGIUM, self.territories.LONDON),
            Convoy(0, Nations.ENGLAND, self.territories.NORTH_SEA, self.territories.BELGIUM, self.territories.LONDON),
        ]
        source = self.territories.BELGIUM
        target = self.territories.LONDON
        result = get_convoy_chains(source, target, orders)

        self.assertTrue([orders[0]] in [result[0].convoys, result[1].convoys])
        self.assertTrue([orders[1]] in [result[0].convoys, result[1].convoys])

    def test_two_two_fleet_chains(self):
        orders = [
            Convoy(0, Nations.ENGLAND, self.territories.MID_ATLANTIC, self.territories.PORTUGAL, self.territories.WALES),
            Convoy(0, Nations.ENGLAND, self.territories.ENGLISH_CHANNEL, self.territories.PORTUGAL, self.territories.WALES),
            Convoy(0, Nations.ENGLAND, self.territories.IRISH_SEA, self.territories.PORTUGAL, self.territories.WALES),
        ]
        source = self.territories.PORTUGAL
        target = self.territories.WALES
        result = get_convoy_chains(source, target, orders)
        self.assertTrue([orders[0], orders[1]] in [result[0].convoys, result[1].convoys])
        self.assertTrue([orders[0], orders[2]] in [result[0].convoys, result[1].convoys])
