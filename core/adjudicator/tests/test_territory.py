
import unittest
from core.adjudicator.state import state
from core.adjudicator.territory import CoastalTerritory, Territory, SeaTerritory, InlandTerritory
from core.adjudicator.piece import Army, Fleet


class TerritoryTestCase(unittest.TestCase):
    def setUp(self):
        state.__init__()


class TestString(TerritoryTestCase):

    def test_string(self):
        t = CoastalTerritory(1, 'London', 'England', [], [])
        self.assertEqual(str(t), 'London')


class TestNeighbours(TerritoryTestCase):

    def test_neighbours(self):
        london = CoastalTerritory(1, 'London', 'England', [2], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [1], [])
        paris = InlandTerritory(3, 'Paris', 'France', [])

        self.assertEqual(london.neighbours, [wales])
        self.assertEqual(wales.neighbours, [london])
        self.assertFalse(paris in london.neighbours)


class TestSharedCoasts(TerritoryTestCase):

    def test_shared_coasts(self):
        london = CoastalTerritory(1, 'London', 'England', [2], [2])
        wales = CoastalTerritory(2, 'Wales', 'England', [1], [1])
        paris = InlandTerritory(3, 'Paris', 'France', [])

        self.assertEqual(london.shared_coasts, [wales])
        self.assertEqual(wales.shared_coasts, [london])
        self.assertFalse(paris in london.neighbours)


class TestAdjacentTo(TerritoryTestCase):

    def test_neighbours(self):
        london = CoastalTerritory(1, 'London', 'England', [2], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [1], [])
        paris = InlandTerritory(3, 'Paris', 'France', [])

        self.assertTrue(london.adjacent_to(wales))
        self.assertFalse(london.adjacent_to(paris))


class TestPiece(TerritoryTestCase):

    def test_piece(self):
        london = CoastalTerritory(1, 'London', 'England', [], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [], [])
        paris = InlandTerritory(3, 'Paris', 'France', [])

        army_london = Army('England', london)
        army_wales = Army('England', wales)

        self.assertEqual(army_london, london.piece)
        self.assertEqual(army_wales, wales.piece)
        self.assertIsNone(paris.piece)


class TestOccupied(TerritoryTestCase):

    def test_occupied(self):
        london = CoastalTerritory(1, 'London', 'England', [], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [], [])
        Army('England', london)

        self.assertTrue(london.occupied)
        self.assertFalse(wales.occupied)


class TestOccupiedBy(TerritoryTestCase):

    def test_occupied_by(self):
        london = CoastalTerritory(1, 'London', 'England', [], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [], [])
        paris = InlandTerritory(3, 'Paris', 'England', [])
        Army('England', london)
        Army('France', paris)

        self.assertTrue(london.occupied_by('England'))
        self.assertFalse(wales.occupied_by('England'))
        self.assertFalse(paris.occupied_by('England'))


class TestAccessibleByPieceType(TerritoryTestCase):

    def test_coastal(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [], [])
        english_channel = SeaTerritory(2, 'English Channel', [])
        brest = CoastalTerritory(3, 'Brest', 'France', [], [])

        army = Army('England', picardy)
        fleet = Fleet('France', english_channel)
        self.assertTrue(brest.accessible_by_piece_type(army))
        self.assertTrue(brest.accessible_by_piece_type(fleet))

    def test_inland(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [], [])
        english_channel = SeaTerritory(2, 'English Channel', [])
        paris = InlandTerritory(3, 'Paris', 'France', [])

        army = Army('England', picardy)
        fleet = Fleet('France', english_channel)
        self.assertTrue(paris.accessible_by_piece_type(army))
        self.assertFalse(paris.accessible_by_piece_type(fleet))

    def test_sea(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [], [])
        english_channel = SeaTerritory(2, 'English Channel', [])
        irish_sea = SeaTerritory(3, 'Irish Sea', [])

        army = Army('England', picardy)
        fleet = Fleet('France', english_channel)
        self.assertFalse(irish_sea.accessible_by_piece_type(army))
        self.assertTrue(irish_sea.accessible_by_piece_type(fleet))
