import unittest

from adjudicator.decisions import Outcomes
from adjudicator.order import Retreat
from adjudicator.piece import Army
from adjudicator.processor import process
from adjudicator.tests.data import NamedCoasts, Nations, Territories

from ..base import AdjudicatorTestCaseMixin


class TestRetreating(AdjudicatorTestCaseMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.territories = Territories(self.state)
        self.named_coasts = NamedCoasts(self.state, self.territories)

    def test_unit_may_not_retreat_from_area_from_which_it_was_attacked(self):
        """
        Well, that would be of course stupid. Still, the adjudicator must be
        tested on this.
        """
        Army(self.state, 0, Nations.ENGLAND, self.territories.NORWAY, attacker_territory=self.territories.SWEDEN),
        orders = [
            Retreat(self.state, 0, Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
        ]
        process(self.state)

        self.assertTrue(orders[0].illegal)
        self.assertEqual(
            orders[0].illegal_verbose,
            'Piece cannot retreat to the territory from which it was attacked.'
        )
        self.assertEqual(orders[0].outcome, Outcomes.FAILS)

    def test_unit_may_not_retreat_to_contested_area(self):
        """
        Stand off prevents retreat to the area.
        """
        self.territories.SWEDEN.contested = True
        Army(self.state, 0, Nations.ENGLAND, self.territories.NORWAY, attacker_territory=self.territories.FINLAND),
        orders = [
            Retreat(self.state, 0, Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
        ]
        process(self.state)

        self.assertTrue(orders[0].illegal)
        self.assertEqual(
            orders[0].illegal_verbose,
            ('Cannot retreat to a territory which was contested on the '
             'previous turn.')
        )
        self.assertEqual(orders[0].outcome, Outcomes.FAILS)

    def test_multiple_retreat_to_the_same_area_causes_disband(self):
        """
        There can only be one unit in an area.
        """
        Army(self.state, 0, Nations.ENGLAND, self.territories.NORWAY, attacker_territory=self.territories.ST_PETERSBURG),
        Army(self.state, 0, Nations.ENGLAND, self.territories.FINLAND, attacker_territory=self.territories.ST_PETERSBURG),
        orders = [
            Retreat(self.state, 0, Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
            Retreat(self.state, 0, Nations.ENGLAND, self.territories.FINLAND, self.territories.SWEDEN),
        ]
        process(self.state)

        self.assertTrue(orders[0].legal)
        self.assertEqual(orders[0].outcome, Outcomes.FAILS)
        self.assertTrue(orders[1].legal)
        self.assertEqual(orders[1].outcome, Outcomes.FAILS)

    def test_three_retreats_to_the_same_area_causes_disband(self):
        """
        When three units retreat to the same area, then all three units are
        disbanded.
        """
        Army(self.state, 0, Nations.ENGLAND, self.territories.NORWAY, attacker_territory=self.territories.ST_PETERSBURG),
        Army(self.state, 0, Nations.ENGLAND, self.territories.FINLAND, attacker_territory=self.territories.ST_PETERSBURG),
        Army(self.state, 0, Nations.RUSSIA, self.territories.DENMARK, attacker_territory=self.territories.KIEL),
        orders = [
            Retreat(self.state, 0, Nations.ENGLAND, self.territories.NORWAY, self.territories.SWEDEN),
            Retreat(self.state, 0, Nations.ENGLAND, self.territories.FINLAND, self.territories.SWEDEN),
            Retreat(self.state, 0, Nations.RUSSIA, self.territories.DENMARK, self.territories.SWEDEN),
        ]
        process(self.state)

        self.assertTrue(orders[0].legal)
        self.assertEqual(orders[0].outcome, Outcomes.FAILS)
        self.assertTrue(orders[1].legal)
        self.assertEqual(orders[1].outcome, Outcomes.FAILS)
        self.assertTrue(orders[2].legal)
        self.assertEqual(orders[2].outcome, Outcomes.FAILS)
