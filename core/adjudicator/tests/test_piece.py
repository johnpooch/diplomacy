import unittest

from core.adjudicator.named_coast import NamedCoast
from core.adjudicator.state import state
from core.adjudicator.order import Move
from core.adjudicator.piece import Army, Fleet, Piece
from core.adjudicator.territory import CoastalTerritory, InlandTerritory, SeaTerritory


class PieceTestCase(unittest.TestCase):
    def setUp(self):
        state.__init__()


class TestOrder(PieceTestCase):

    def test_order_exists(self):
        london = CoastalTerritory(1, "London", "England", [], [])
        wales = CoastalTerritory(2, "Wales", "England", [], [])
        army = Army("England", london)
        london_move = Move("England", london, wales)

        self.assertEqual(army.order, london_move)

    def test_order_does_not_exist(self):
        pass


class TestCanReachArmy(PieceTestCase):

    def setUp(self):

        self.paris = InlandTerritory(1, "Paris", "France", [7])
        self.london = CoastalTerritory(2, "London", "England", [3, 6], [3])
        self.wales = CoastalTerritory(3, "Wales", "England", [2, 6], [2])
        self.munich = InlandTerritory(4, "Munich", "Germany", [5])
        self.silesia = InlandTerritory(5, "Silesia", "Germany", [4])
        self.english_channel = SeaTerritory(6, "English Channel", [2, 3])
        self.brest = CoastalTerritory(7, "Brest", "France", [1, 6], [])

    def test_army_inland_to_neighbouring_inland(self):
        army = Army("England", self.munich)
        self.assertTrue(army.can_reach(self.silesia))

    def test_army_inland_to_neighbouring_coastal(self):
        army = Army("England", self.paris)
        self.assertTrue(army.can_reach(self.brest))

    def test_army_coastal_to_neighbouring_inland(self):
        army = Army("England", self.brest)
        self.assertTrue(army.can_reach(self.paris))

    def test_army_coastal_to_neighbouring_coastal(self):
        army = Army("England", self.london)
        self.assertTrue(army.can_reach(self.wales))

    def test_army_coastal_to_neighbouring_sea(self):
        army = Army("England", self.wales)
        self.assertFalse(army.can_reach(self.english_channel))

    def test_army_coastal_to_non_neighbouring_coastal(self):
        army = Army("England", self.brest)
        self.assertTrue(army.can_reach(self.london))

    def test_army_coastal_to_non_neighbouring_inland(self):
        army = Army("England", self.wales)
        self.assertFalse(army.can_reach(self.paris))


class TestCanReachFleet(PieceTestCase):

    def setUp(self):

        self.paris = InlandTerritory(1, "Paris", "France", [7])
        self.london = CoastalTerritory(2, "London", "England", [3, 6], [3])
        self.wales = CoastalTerritory(3, "Wales", "England", [2, 6], [2])
        self.english_channel = SeaTerritory(6, "English Channel", [2, 3])
        self.brest = CoastalTerritory(7, "Brest", "France", [1, 6], [])
        self.rome = CoastalTerritory(8, "Rome", "Italy", [9], [])
        self.apulia = CoastalTerritory(9, "Apulia", "Italy", [8], [])

        self.spain = CoastalTerritory(
            10, "Spain", None, [11, 12, 13, 14], [11, 12])
        self.gascony = CoastalTerritory(11, "Gascony", "France", [10], [])
        self.marseilles = CoastalTerritory(
            12, "Marseilles", "France", [10], [10])
        self.mid_atlantic = SeaTerritory(13, "Mid Atlantic", [10])
        self.gulf_of_lyon = SeaTerritory(14, "Gulf of Lyon", [10])
        self.spain_north_coast = NamedCoast(
            1, "North Coast", self.spain, [self.gascony, self.mid_atlantic])
        self.spain_south_coast = NamedCoast(
            2, "South Coast", self.spain, [self.marseilles, self.gulf_of_lyon, self.marseilles])

    def test_fleet_coastal_to_neighbouring_inland(self):
        fleet = Fleet("England", self.brest)
        self.assertFalse(fleet.can_reach(self.paris))

    def test_fleet_coastal_to_neighbouring_coastal_shared_coast(self):
        fleet = Fleet("England", self.london)
        self.assertTrue(fleet.can_reach(self.wales))

    def test_fleet_coastal_to_neighbouring_sea(self):
        fleet = Fleet("England", self.wales)
        self.assertTrue(fleet.can_reach(self.english_channel))

    def test_fleet_coastal_to_non_neighbouring_coastal(self):
        fleet = Fleet("England", self.brest)
        self.assertFalse(fleet.can_reach(self.london))

    def test_fleet_coastal_to_non_neighbouring_inland(self):
        fleet = Fleet("England", self.wales)
        self.assertFalse(fleet.can_reach(self.paris))

    def test_fleet_coastal_to_neighbouring_coastal_unshared_coast(self):
        fleet = Fleet("England", self.rome)
        self.assertFalse(fleet.can_reach(self.apulia))

    def test_named_coast_to_coastal(self):
        fleet = Fleet("England", self.spain, self.spain_north_coast)
        self.assertTrue(fleet.can_reach(self.gascony))

    def test_named_coast_to_coastal_non_neighbouring(self):
        fleet = Fleet("England", self.spain, self.spain_north_coast)
        self.assertFalse(fleet.can_reach(self.marseilles))

    def test_named_coast_to_sea(self):
        fleet = Fleet("England", self.spain, self.spain_north_coast)
        self.assertTrue(fleet.can_reach(self.mid_atlantic))

    def test_named_coast_to_sea_non_neighbouring(self):
        fleet = Fleet("England", self.spain, self.spain_north_coast)
        self.assertFalse(fleet.can_reach(self.gulf_of_lyon))

    def test_sea_to_named_coast(self):
        fleet = Fleet("England", self.gulf_of_lyon)
        self.assertTrue(fleet.can_reach(self.spain, self.spain_south_coast))

    def test_sea_to_named_coast_non_neighbouring(self):
        fleet = Fleet("England", self.gulf_of_lyon)
        self.assertFalse(fleet.can_reach(self.spain, self.spain_north_coast))

    def coastal_to_named_coast(self):
        fleet = Fleet("England", self.marseilles)
        self.assertTrue(fleet.can_reach(self.spain, self.spain_south_coast))

    def coastal_to_named_coast_non_neighbouring(self):
        fleet = Fleet("England", self.marseilles)
        self.assertFalse(fleet.can_reach(self.spain, self.spain_north_coast))

    def coastal_to_complex_no_named_coast(self):
        fleet = Fleet("England", self.marseilles)
        with self.assertRaises(ValueError):
            fleet.can_reach(self.spain)
