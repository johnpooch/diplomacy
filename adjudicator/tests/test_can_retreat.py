import unittest

from adjudicator.piece import Army, Fleet
from adjudicator.tests.data import NamedCoasts, Nations, Territories

from .base import AdjudicatorTestCaseMixin


class TestCanRetreat(AdjudicatorTestCaseMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.territories = Territories(self.state)
        self.named_coasts = NamedCoasts(self.state, self.territories)

    def test_army_all_neighbouring_land_occupied(self):
        retreating_army = Army(self.state, 0, Nations.FRANCE, self.territories.PORTUGAL)
        Army(self.state, 0, Nations.ITALY, self.territories.SPAIN)
        self.assertFalse(retreating_army.can_retreat())

    def test_army_neighbouring_land_contested(self):
        retreating_army = Army(self.state, 0, Nations.FRANCE, self.territories.BREST)
        Army(self.state, 0, Nations.ITALY, self.territories.GASCONY)
        Army(self.state, 0, Nations.ITALY, self.territories.PICARDY)
        paris = self.state.get_territory('paris')
        paris.bounce_occurred = True
        self.assertFalse(retreating_army.can_retreat())

    def test_fleet_all_neighbouring_seas_occupied(self):
        retreating_fleet = Fleet(self.state, 0, Nations.FRANCE, self.territories.BARRENTS_SEA)
        Army(self.state, 0, Nations.RUSSIA, self.territories.ST_PETERSBURG)
        Army(self.state, 0, Nations.RUSSIA, self.territories.NORWAY)
        Fleet(self.state, 0, Nations.RUSSIA, self.territories.NORWEGIAN_SEA)
        self.assertFalse(retreating_fleet.can_retreat())

    def test_fleet_can_retreat_to_coast(self):
        retreating_fleet = Fleet(self.state, 0, Nations.FRANCE, self.territories.BARRENTS_SEA)
        Army(self.state, 0, Nations.RUSSIA, self.territories.NORWAY)
        Fleet(self.state, 0, Nations.RUSSIA, self.territories.NORWEGIAN_SEA)
        self.assertTrue(retreating_fleet.can_retreat())
