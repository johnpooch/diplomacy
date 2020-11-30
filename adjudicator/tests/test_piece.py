import unittest

from adjudicator.named_coast import NamedCoast
from adjudicator.order import Move
from adjudicator.piece import Army, Fleet
from adjudicator.state import State
from adjudicator.territory import CoastalTerritory, InlandTerritory, SeaTerritory

from .base import AdjudicatorTestCaseMixin


class TestOrder(AdjudicatorTestCaseMixin, unittest.TestCase):

    def test_order_exists(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [], [])
        wales = CoastalTerritory(self.state, 2, 'Wales', 'England', [], [])
        army = Army(self.state, 0, 'England', london)
        london_move = Move(self.state, 0, 'England', london, wales)

        self.assertEqual(army.order, london_move)


class TestCanReachArmy(AdjudicatorTestCaseMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.paris = InlandTerritory(self.state, 1, 'Paris', 'France', [7])
        self.london = CoastalTerritory(self.state, 2, 'London', 'England', [3, 6], [3])
        self.wales = CoastalTerritory(self.state, 3, 'Wales', 'England', [2, 6], [2])
        self.munich = InlandTerritory(self.state, 4, 'Munich', 'Germany', [5])
        self.silesia = InlandTerritory(self.state, 5, 'Silesia', 'Germany', [4])
        self.english_channel = SeaTerritory(self.state, 6, 'English Channel', [2, 3])
        self.brest = CoastalTerritory(self.state, 7, 'Brest', 'France', [1, 6], [])

    def test_army_inland_to_neighbouring_inland(self):
        army = Army(self.state, 0, 'England', self.munich)
        self.state.register(army)
        self.assertTrue(army.can_reach(self.silesia))

    def test_army_inland_to_neighbouring_coastal(self):
        army = Army(self.state, 0, 'England', self.paris)
        self.state.register(army)
        self.assertTrue(army.can_reach(self.brest))

    def test_army_coastal_to_neighbouring_inland(self):
        army = Army(self.state, 0, 'England', self.brest)
        self.state.register(army)
        self.assertTrue(army.can_reach(self.paris))

    def test_army_coastal_to_neighbouring_coastal(self):
        army = Army(self.state, 0, 'England', self.london)
        self.state.register(army)
        self.assertTrue(army.can_reach(self.wales))

    def test_army_coastal_to_neighbouring_sea(self):
        army = Army(self.state, 0, 'England', self.wales)
        self.state.register(army)
        self.assertFalse(army.can_reach(self.english_channel))

    def test_army_coastal_to_non_neighbouring_coastal(self):
        army = Army(self.state, 0, 'England', self.brest)
        self.state.register(army)
        self.assertTrue(army.can_reach(self.london))

    def test_army_coastal_to_non_neighbouring_inland(self):
        army = Army(self.state, 0, 'England', self.wales)
        self.state.register(army)
        self.assertFalse(army.can_reach(self.paris))


class TestCanReachFleet(AdjudicatorTestCaseMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.paris = InlandTerritory(self.state, 1, 'Paris', 'France', [7])
        self.london = CoastalTerritory(self.state, 2, 'London', 'England', [3, 6], [3])
        self.wales = CoastalTerritory(self.state, 3, 'Wales', 'England', [2, 6], [2])
        self.english_channel = SeaTerritory(self.state, 6, 'English Channel', [2, 3])
        self.brest = CoastalTerritory(self.state, 7, 'Brest', 'France', [1, 6], [])
        self.rome = CoastalTerritory(self.state, 8, 'Rome', 'Italy', [9], [])
        self.apulia = CoastalTerritory(self.state, 9, 'Apulia', 'Italy', [8], [])

        self.spain = CoastalTerritory(self.state, 
            10, 'Spain', None, [11, 12, 13, 14], [11, 12])
        self.gascony = CoastalTerritory(self.state, 11, 'Gascony', 'France', [10], [])
        self.marseilles = CoastalTerritory(self.state, 
            12, 'Marseilles', 'France', [10], [10])
        self.mid_atlantic = SeaTerritory(self.state, 13, 'Mid Atlantic', [10])
        self.gulf_of_lyon = SeaTerritory(self.state, 14, 'Gulf of Lyon', [10])
        self.spain_north_coast = NamedCoast(self.state, 
            1, 'North Coast', self.spain, [self.gascony, self.mid_atlantic])
        self.spain_south_coast = NamedCoast(self.state, 
            2, 'South Coast', self.spain, [self.marseilles, self.gulf_of_lyon, self.marseilles])

        to_register = [self.paris, self.london, self.wales,
                       self.english_channel, self.brest, self.rome,
                       self.apulia, self.spain, self.gascony, self.marseilles,
                       self.mid_atlantic, self.gulf_of_lyon,
                       self.spain_north_coast, self.spain_south_coast]
        [self.state.register(o) for o in to_register]

    def test_fleet_coastal_to_neighbouring_inland(self):
        fleet = Fleet(self.state, 0, 'England', self.brest)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.paris))

    def test_fleet_coastal_to_neighbouring_coastal_shared_coast(self):
        fleet = Fleet(self.state, 0, 'England', self.london)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.wales))

    def test_fleet_coastal_to_neighbouring_sea(self):
        fleet = Fleet(self.state, 0, 'England', self.wales)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.english_channel))

    def test_fleet_coastal_to_non_neighbouring_coastal(self):
        fleet = Fleet(self.state, 0, 'England', self.brest)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.london))

    def test_fleet_coastal_to_non_neighbouring_inland(self):
        fleet = Fleet(self.state, 0, 'England', self.wales)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.paris))

    def test_fleet_coastal_to_neighbouring_coastal_unshared_coast(self):
        fleet = Fleet(self.state, 0, 'England', self.rome)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.apulia))

    def test_named_coast_to_coastal(self):
        fleet = Fleet(self.state, 0, 'England', self.spain, self.spain_north_coast)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.gascony))

    def test_named_coast_to_coastal_non_neighbouring(self):
        fleet = Fleet(self.state, 0, 'England', self.spain, self.spain_north_coast)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.marseilles))

    def test_named_coast_to_sea(self):
        fleet = Fleet(self.state, 0, 'England', self.spain, self.spain_north_coast)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.mid_atlantic))

    def test_named_coast_to_sea_non_neighbouring(self):
        fleet = Fleet(self.state, 0, 'England', self.spain, self.spain_north_coast)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.gulf_of_lyon))

    def test_sea_to_named_coast(self):
        fleet = Fleet(self.state, 0, 'England', self.gulf_of_lyon)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.spain, self.spain_south_coast))

    def test_sea_to_named_coast_non_neighbouring(self):
        fleet = Fleet(self.state, 0, 'England', self.gulf_of_lyon)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.spain, self.spain_north_coast))

    def coastal_to_named_coast(self):
        fleet = Fleet(self.state, 0, 'England', self.marseilles)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.spain, self.spain_south_coast))

    def coastal_to_named_coast_non_neighbouring(self):
        fleet = Fleet(self.state, 0, 'England', self.marseilles)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.spain, self.spain_north_coast))

    def coastal_to_complex_no_named_coast(self):
        fleet = Fleet(self.state, 0, 'England', self.marseilles)
        self.state.register(fleet)
        with self.assertRaises(ValueError):
            fleet.can_reach(self.spain)
