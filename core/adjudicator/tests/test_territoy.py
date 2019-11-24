import unittest
from territory import CoastalTerritory, Territory


class TerritoryTestCase(unittest.TestCase):
    def setUp(self):
        Territory.all_territories = []


class TestString(TerritoryTestCase):

    def test_string(self):
        t = Territory(1, 'London', 'England', [])
        self.assertEqual(str(t), 'London')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


class TestNeighbours(TerritoryTestCase):

    def test_neighbours(self):
        london = Territory(1, 'London', 'England', [2])
        wales = Territory(2, 'Wales', 'England', [1])
        paris = Territory(3, 'Paris', 'France', [])

        self.assertEqual(london.neighbours, [wales])
        self.assertEqual(wales.neighbours, [london])
        self.assertFalse(paris in london.neighbours)


class TestSharedCoasts(TerritoryTestCase):

    def test_shared_coasts(self):
        london = CoastalTerritory(1, 'London', 'England', [2], [2])
        wales = CoastalTerritory(2, 'Wales', 'England', [1], [1])
        paris = Territory(3, 'Paris', 'France', [])

        self.assertEqual(london.shared_coasts, [wales])
        self.assertEqual(wales.shared_coasts, [london])
        self.assertFalse(paris in london.neighbours)


class TestAdjacentTo(TerritoryTestCase):

    def test_neighbours(self):
        london = Territory(1, 'London', 'England', [2])
        wales = Territory(2, 'Wales', 'England', [1])
        paris = Territory(3, 'Paris', 'France', [])

        self.assertTrue(london.adjacent_to(wales))
        self.assertFalse(london.adjacent_to(paris))
