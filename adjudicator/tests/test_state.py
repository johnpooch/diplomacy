import unittest

from adjudicator.named_coast import NamedCoast
from adjudicator.order import Hold
from adjudicator.piece import Army
from adjudicator.state import State
from adjudicator.territory import CoastalTerritory, InlandTerritory
from adjudicator.tests.data import Nations


class TestState(unittest.TestCase):

    def test_register_piece_updates_territory(self):
        state = State()
        paris = InlandTerritory(1, 'paris', Nations.FRANCE, [])
        army_paris = Army(0, Nations.FRANCE, paris)

        state.register(paris)
        state.register(army_paris)

        self.assertEqual(paris.piece, army_paris)

    def test_register_territory_updates_neighbours(self):
        state = State()
        paris = InlandTerritory(1, 'paris', Nations.FRANCE, [2, 3])
        burgundy = InlandTerritory(2, 'burgundy', Nations.FRANCE, [1, 3])
        gascony = InlandTerritory(3, 'gascony', Nations.FRANCE, [1, 2])

        state.register(paris)
        state.register(burgundy)
        state.register(gascony)

        self.assertTrue(paris in burgundy.neighbours)
        self.assertTrue(paris in gascony.neighbours)
        self.assertTrue(burgundy in paris.neighbours)
        self.assertTrue(burgundy in gascony.neighbours)
        self.assertTrue(gascony in paris.neighbours)
        self.assertTrue(gascony in burgundy.neighbours)

    def test_register_territory_updates_shared_coasts(self):
        state = State()
        rome = CoastalTerritory(1, 'rome', Nations.ITALY, [2, 4], [2, 3])
        naples = CoastalTerritory(2, 'naples', Nations.ITALY, [1], [1])
        tuscany = CoastalTerritory(3, 'tuscany', Nations.ITALY, [1, 4], [1])
        venice = CoastalTerritory(4, 'venice', Nations.ITALY, [1, 3], [])

        state.register(rome)
        state.register(naples)
        state.register(tuscany)
        state.register(venice)

        self.assertTrue(all([t in rome.neighbours for t in [naples, venice]]))
        self.assertEqual({rome}, naples.neighbours)
        self.assertTrue(all([t in tuscany.neighbours for t in [rome, venice]]))
        self.assertTrue(all([t in venice.neighbours for t in [rome, tuscany]]))

        self.assertEqual(rome.shared_coasts, {naples, tuscany})
        self.assertEqual(naples.shared_coasts, {rome})
        self.assertEqual(tuscany.shared_coasts, {rome})
        self.assertEqual(venice.shared_coasts, set())

    def test_register_order_updates_piece_order(self):
        state = State()
        paris = InlandTerritory(1, 'paris', Nations.FRANCE, [])
        army_paris = Army(0, Nations.FRANCE, paris)
        hold = Hold(0, Nations.FRANCE, paris)

        state.register(paris)
        state.register(army_paris)
        state.register(hold)

        self.assertEqual(army_paris.order, hold)
        self.assertEqual(hold.piece, army_paris)

    def test_register_named_coast_updates_territory(self):
        state = State()
        spain = CoastalTerritory(1, 'spain', None, [], [])
        spain_nc = NamedCoast(1, 'spain sc', spain, [])

        state.register(spain)
        state.register(spain_nc)

        self.assertTrue(spain_nc in spain.named_coasts)
