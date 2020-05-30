import unittest

from adjudicator.piece import Army, Fleet
from adjudicator.state import State
from adjudicator.tests.data import NamedCoasts, Nations, Territories, register_all


class TestCanRetreat(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.territories = Territories()
        self.named_coasts = NamedCoasts(self.territories)
        self.state = register_all(self.state, self.territories, self.named_coasts)

    def test_army_all_neighbouring_land_occupied(self):
        retreating_army = Army(0, Nations.FRANCE, self.territories.PORTUGAL)
        spain_army = Army(0, Nations.ITALY, self.territories.SPAIN)
        self.state.register(retreating_army, spain_army)
        self.state.post_register_updates()
        self.assertFalse(retreating_army.can_retreat())

    def test_army_neighbouring_land_contested(self):
        retreating_army = Army(0, Nations.FRANCE, self.territories.BREST)
        gascony_army = Army(0, Nations.ITALY, self.territories.GASCONY)
        picary_army = Army(0, Nations.ITALY, self.territories.PICARDY)
        self.state.register(retreating_army, gascony_army, picary_army)
        self.state.post_register_updates()
        paris = self.state.get_territory('paris')
        paris.bounce_occurred = True
        self.assertFalse(retreating_army.can_retreat())

    def test_fleet_all_neighbouring_seas_occupied(self):
        retreating_fleet = Fleet(0, Nations.FRANCE, self.territories.BARRENTS_SEA)
        stp_army = Army(0, Nations.RUSSIA, self.territories.ST_PETERSBURG)
        norway_army = Army(0, Nations.RUSSIA, self.territories.NORWAY)
        norwegian_sea_fleet = Fleet(0, Nations.RUSSIA, self.territories.NORWEGIAN_SEA)
        self.state.register(retreating_fleet, stp_army, norway_army, norwegian_sea_fleet)
        self.state.post_register_updates()
        self.assertFalse(retreating_fleet.can_retreat())

    def test_fleet_can_retreat_to_coast(self):
        retreating_fleet = Fleet(0, Nations.FRANCE, self.territories.BARRENTS_SEA)
        norway_army = Army(0, Nations.RUSSIA, self.territories.NORWAY)
        norwegian_sea_fleet = Fleet(0, Nations.RUSSIA, self.territories.NORWEGIAN_SEA)
        self.state.register(retreating_fleet, norway_army, norwegian_sea_fleet)
        self.state.post_register_updates()
        self.assertTrue(retreating_fleet.can_retreat())
