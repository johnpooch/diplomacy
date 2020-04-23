import unittest

from adjudicator import illegal_messages
from adjudicator.decisions import Outcomes
from adjudicator.order import Retreat
from adjudicator.piece import Army
from adjudicator.processor import process
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestRetreating(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

    def test_unit_may_not_retreat_from_area_from_which_it_was_attacked(self):
        """
        Well, that would be of course stupid. Still, the adjudicator must be
        tested on this.
        """
        pieces = [
            Army(0, Nations.ENGLAND, self.territories.NORWAY, attacker_territory=self.territories.SWEDEN),
        ]
        orders = [
            Retreat(0, Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(orders[0].illegal_message, illegal_messages.R001)
        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)

    def test_unit_may_not_retreat_to_contested_area(self):
        """
        Stand off prevents retreat to the area.
        """
        self.territories.SWEDEN.contested = True
        pieces = [
            Army(0, Nations.ENGLAND, self.territories.NORWAY, attacker_territory=self.territories.FINLAND),
        ]
        orders = [
            Retreat(0, Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.ILLEGAL)
        self.assertEqual(orders[0].illegal_message, illegal_messages.R005)
        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)

    def test_multiple_retreat_to_the_same_area_causes_disband(self):
        """
        There can only be one unit in an area.
        """
        pieces = [
            Army(0, Nations.ENGLAND, self.territories.NORWAY, attacker_territory=self.territories.ST_PETERSBURG),
            Army(0, Nations.ENGLAND, self.territories.FINLAND, attacker_territory=self.territories.ST_PETERSBURG),
        ]
        orders = [
            Retreat(0, Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
            Retreat(0, Nations.ENGLAND, self.territories.FINLAND, self.territories.SWEDEN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.LEGAL)
        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].legal_decision, Outcomes.LEGAL)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)

    def test_three_retreats_to_the_same_area_causes_disband(self):
        """
        When three units retreat to the same area, then all three units are
        disbanded.
        """
        pieces = [
            Army(0, Nations.ENGLAND, self.territories.NORWAY, attacker_territory=self.territories.ST_PETERSBURG),
            Army(0, Nations.ENGLAND, self.territories.FINLAND, attacker_territory=self.territories.ST_PETERSBURG),
            Army(0, Nations.RUSSIA, self.territories.DENMARK, attacker_territory=self.territories.KIEL),
        ]
        orders = [
            Retreat(0, Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
            Retreat(0, Nations.ENGLAND, self.territories.FINLAND, self.territories.SWEDEN),
            Retreat(0, Nations.RUSSIA, self.territories.DENMARK, self.territories.SWEDEN),
        ]
        self.state.register(*pieces, *orders)
        self.state.post_register_updates()
        process(self.state)

        self.assertEqual(orders[0].legal_decision, Outcomes.LEGAL)
        self.assertEqual(orders[0].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[1].legal_decision, Outcomes.LEGAL)
        self.assertEqual(orders[1].move_decision, Outcomes.FAILS)
        self.assertEqual(orders[2].legal_decision, Outcomes.LEGAL)
        self.assertEqual(orders[2].move_decision, Outcomes.FAILS)
