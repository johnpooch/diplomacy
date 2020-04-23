import unittest

from adjudicator.named_coast import NamedCoast
from adjudicator.decisions import Outcomes
from adjudicator.order import Move
from adjudicator.piece import Army, Fleet
from adjudicator.state import State
from adjudicator.territory import CoastalTerritory, InlandTerritory, SeaTerritory


class TestOrder(unittest.TestCase):

    def test_order_exists(self):
        state = State()
        london = CoastalTerritory(1, 'London', 'England', [], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [], [])
        army = Army(0, 'England', london)
        london_move = Move(0, 'England', london, wales)

        to_register = [london, wales, army, london_move]
        [state.register(o) for o in to_register]

        self.assertEqual(army.order, london_move)


class TestCanReachArmy(unittest.TestCase):

    def setUp(self):

        self.state = State()
        self.paris = InlandTerritory(1, 'Paris', 'France', [7])
        self.london = CoastalTerritory(2, 'London', 'England', [3, 6], [3])
        self.wales = CoastalTerritory(3, 'Wales', 'England', [2, 6], [2])
        self.munich = InlandTerritory(4, 'Munich', 'Germany', [5])
        self.silesia = InlandTerritory(5, 'Silesia', 'Germany', [4])
        self.english_channel = SeaTerritory(6, 'English Channel', [2, 3])
        self.brest = CoastalTerritory(7, 'Brest', 'France', [1, 6], [])

        to_register = [self.paris, self.london, self.wales, self.munich,
                       self.silesia, self.english_channel, self.brest]
        [self.state.register(o) for o in to_register]

    def test_army_inland_to_neighbouring_inland(self):
        army = Army(0, 'England', self.munich)
        self.state.register(army)
        self.assertTrue(army.can_reach(self.silesia))

    def test_army_inland_to_neighbouring_coastal(self):
        army = Army(0, 'England', self.paris)
        self.state.register(army)
        self.assertTrue(army.can_reach(self.brest))

    def test_army_coastal_to_neighbouring_inland(self):
        army = Army(0, 'England', self.brest)
        self.state.register(army)
        self.assertTrue(army.can_reach(self.paris))

    def test_army_coastal_to_neighbouring_coastal(self):
        army = Army(0, 'England', self.london)
        self.state.register(army)
        self.assertTrue(army.can_reach(self.wales))

    def test_army_coastal_to_neighbouring_sea(self):
        army = Army(0, 'England', self.wales)
        self.state.register(army)
        self.assertFalse(army.can_reach(self.english_channel))

    def test_army_coastal_to_non_neighbouring_coastal(self):
        army = Army(0, 'England', self.brest)
        self.state.register(army)
        self.assertTrue(army.can_reach(self.london))

    def test_army_coastal_to_non_neighbouring_inland(self):
        army = Army(0, 'England', self.wales)
        self.state.register(army)
        self.assertFalse(army.can_reach(self.paris))


class TestCanReachFleet(unittest.TestCase):

    def setUp(self):

        self.state = State()
        self.paris = InlandTerritory(1, 'Paris', 'France', [7])
        self.london = CoastalTerritory(2, 'London', 'England', [3, 6], [3])
        self.wales = CoastalTerritory(3, 'Wales', 'England', [2, 6], [2])
        self.english_channel = SeaTerritory(6, 'English Channel', [2, 3])
        self.brest = CoastalTerritory(7, 'Brest', 'France', [1, 6], [])
        self.rome = CoastalTerritory(8, 'Rome', 'Italy', [9], [])
        self.apulia = CoastalTerritory(9, 'Apulia', 'Italy', [8], [])

        self.spain = CoastalTerritory(
            10, 'Spain', None, [11, 12, 13, 14], [11, 12])
        self.gascony = CoastalTerritory(11, 'Gascony', 'France', [10], [])
        self.marseilles = CoastalTerritory(
            12, 'Marseilles', 'France', [10], [10])
        self.mid_atlantic = SeaTerritory(13, 'Mid Atlantic', [10])
        self.gulf_of_lyon = SeaTerritory(14, 'Gulf of Lyon', [10])
        self.spain_north_coast = NamedCoast(
            1, 'North Coast', self.spain, [self.gascony, self.mid_atlantic])
        self.spain_south_coast = NamedCoast(
            2, 'South Coast', self.spain, [self.marseilles, self.gulf_of_lyon, self.marseilles])

        to_register = [self.paris, self.london, self.wales,
                       self.english_channel, self.brest, self.rome,
                       self.apulia, self.spain, self.gascony, self.marseilles,
                       self.mid_atlantic, self.gulf_of_lyon,
                       self.spain_north_coast, self.spain_south_coast]
        [self.state.register(o) for o in to_register]

    def test_fleet_coastal_to_neighbouring_inland(self):
        fleet = Fleet(0, 'England', self.brest)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.paris))

    def test_fleet_coastal_to_neighbouring_coastal_shared_coast(self):
        fleet = Fleet(0, 'England', self.london)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.wales))

    def test_fleet_coastal_to_neighbouring_sea(self):
        fleet = Fleet(0, 'England', self.wales)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.english_channel))

    def test_fleet_coastal_to_non_neighbouring_coastal(self):
        fleet = Fleet(0, 'England', self.brest)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.london))

    def test_fleet_coastal_to_non_neighbouring_inland(self):
        fleet = Fleet(0, 'England', self.wales)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.paris))

    def test_fleet_coastal_to_neighbouring_coastal_unshared_coast(self):
        fleet = Fleet(0, 'England', self.rome)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.apulia))

    def test_named_coast_to_coastal(self):
        fleet = Fleet(0, 'England', self.spain, self.spain_north_coast)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.gascony))

    def test_named_coast_to_coastal_non_neighbouring(self):
        fleet = Fleet(0, 'England', self.spain, self.spain_north_coast)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.marseilles))

    def test_named_coast_to_sea(self):
        fleet = Fleet(0, 'England', self.spain, self.spain_north_coast)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.mid_atlantic))

    def test_named_coast_to_sea_non_neighbouring(self):
        fleet = Fleet(0, 'England', self.spain, self.spain_north_coast)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.gulf_of_lyon))

    def test_sea_to_named_coast(self):
        fleet = Fleet(0, 'England', self.gulf_of_lyon)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.spain, self.spain_south_coast))

    def test_sea_to_named_coast_non_neighbouring(self):
        fleet = Fleet(0, 'England', self.gulf_of_lyon)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.spain, self.spain_north_coast))

    def coastal_to_named_coast(self):
        fleet = Fleet(0, 'England', self.marseilles)
        self.state.register(fleet)
        self.assertTrue(fleet.can_reach(self.spain, self.spain_south_coast))

    def coastal_to_named_coast_non_neighbouring(self):
        fleet = Fleet(0, 'England', self.marseilles)
        self.state.register(fleet)
        self.assertFalse(fleet.can_reach(self.spain, self.spain_north_coast))

    def coastal_to_complex_no_named_coast(self):
        fleet = Fleet(0, 'England', self.marseilles)
        self.state.register(fleet)
        with self.assertRaises(ValueError):
            fleet.can_reach(self.spain)


class TestToDict(unittest.TestCase):

    def setUp(self):
        self.state = State()
        self.portugal = CoastalTerritory(11, 'Portugal', None, [], [])
        self.spain = CoastalTerritory(10, 'Spain', None, [], [])
        self.spain_south_coast = NamedCoast(2, 'South Coast', self.spain, [])

        to_register = [self.spain, self.spain_south_coast]
        [self.state.register(o) for o in to_register]

    def test_to_dict_dislodged(self):
        fleet = Fleet(1, 'England', self.spain, self.spain_south_coast)
        attacking_fleet = Fleet(2, 'France', self.portugal)
        fleet.dislodged_decision = Outcomes.DISLODGED
        fleet.dislodged_by = attacking_fleet
        fleet.attacker_territory = self.portugal

        self.assertEqual(
            fleet.to_dict(),
            {
                'id': 1,
                'dislodged_decision': 'dislodged',
                'dislodged_by': 2,
                'attacker_territory': 11,
            }
        )

    def test_to_dict_not_dislodged(self):
        fleet = Fleet(1, 'England', self.spain, self.spain_south_coast)
        fleet.dislodged_decision = Outcomes.SUSTAINS

        self.assertEqual(
            fleet.to_dict(),
            {
                'id': 1,
                'dislodged_decision': 'sustains',
                'dislodged_by': None,
                'attacker_territory': None,
            }
        )
