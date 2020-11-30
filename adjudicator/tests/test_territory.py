import unittest

from adjudicator.named_coast import NamedCoast
from adjudicator.order import Move, Support
from adjudicator.territory import CoastalTerritory, SeaTerritory, InlandTerritory
from adjudicator.piece import Army, Fleet

from .base import AdjudicatorTestCaseMixin


class TerritoryTestCase(AdjudicatorTestCaseMixin, unittest.TestCase):
    pass


class TestString(TerritoryTestCase):

    def test_string(self):
        t = CoastalTerritory(self.state, 1, 'London', 'England', [], [])
        self.assertEqual(str(t), 'London')


class TestNeighbours(TerritoryTestCase):

    state_path = 'adjudicator.territory.state'

    def test_neighbours(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [2], [])
        wales = CoastalTerritory(self.state, 2, 'Wales', 'England', [1], [])
        paris = InlandTerritory(self.state, 3, 'Paris', 'France', [])

        self.assertEqual(london.neighbours, [wales])
        self.assertEqual(wales.neighbours, [london])
        self.assertFalse(paris in london.neighbours)


class TestSharedCoasts(TerritoryTestCase):

    def test_shared_coasts(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [2], [2])
        wales = CoastalTerritory(self.state, 2, 'Wales', 'England', [1], [1])
        paris = InlandTerritory(self.state, 3, 'Paris', 'France', [])

        self.assertEqual(london.shared_coasts, [wales])
        self.assertEqual(wales.shared_coasts, [london])
        self.assertFalse(paris in london.neighbours)


class TestAdjacentTo(TerritoryTestCase):

    def test_neighbours(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [2], [])
        wales = CoastalTerritory(self.state, 2, 'Wales', 'England', [1], [])
        paris = InlandTerritory(self.state, 3, 'Paris', 'France', [])

        self.assertTrue(london.adjacent_to(wales))
        self.assertFalse(london.adjacent_to(paris))


class TestPiece(TerritoryTestCase):

    def test_piece(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [], [])
        wales = CoastalTerritory(self.state, 2, 'Wales', 'England', [], [])
        paris = InlandTerritory(self.state, 3, 'Paris', 'France', [])

        army_london = Army(self.state, 0, 'England', london)
        army_wales = Army(self.state, 0, 'England', wales)

        self.assertEqual(army_london, london.piece)
        self.assertEqual(army_wales, wales.piece)
        self.assertIsNone(paris.piece)


class TestFriendlyPieceExists(TerritoryTestCase):

    def test_friendly_piece_exists(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [], [])
        wales = CoastalTerritory(self.state, 2, 'Wales', 'England', [], [])
        paris = InlandTerritory(self.state, 3, 'Paris', 'France', [])

        Army(self.state, 0, 'England', london)
        Army(self.state, 0, 'France', wales)

        self.assertTrue(london.friendly_piece_exists('England'))
        self.assertFalse(wales.friendly_piece_exists('England'))
        self.assertFalse(paris.friendly_piece_exists('England'))


class TestOccupied(TerritoryTestCase):

    def test_occupied(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [], [])
        wales = CoastalTerritory(self.state, 2, 'Wales', 'England', [], [])

        Army(self.state, 0, 'England', london)

        self.assertTrue(london.occupied)
        self.assertFalse(wales.occupied)


class TestOccupiedBy(TerritoryTestCase):

    def test_occupied_by(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [], [])
        wales = CoastalTerritory(self.state, 2, 'Wales', 'England', [], [])
        paris = InlandTerritory(self.state, 3, 'Paris', 'England', [])

        Army(self.state, 0, 'England', london)
        Army(self.state, 0, 'France', paris)

        self.assertTrue(london.occupied_by('England'))
        self.assertFalse(wales.occupied_by('England'))
        self.assertFalse(paris.occupied_by('England'))


class TestAccessibleByPieceType(TerritoryTestCase):

    def test_coastal(self):
        picardy = CoastalTerritory(self.state, 1, 'Picardy', 'France', [], [])
        english_channel = SeaTerritory(self.state, 2, 'English Channel', [])
        brest = CoastalTerritory(self.state, 3, 'Brest', 'France', [], [])

        army = Army(self.state, 0, 'England', picardy)
        fleet = Fleet(self.state, 0, 'France', english_channel)

        self.assertTrue(brest.accessible_by_piece_type(army))
        self.assertTrue(brest.accessible_by_piece_type(fleet))

    def test_inland(self):
        picardy = CoastalTerritory(self.state, 1, 'Picardy', 'France', [], [])
        english_channel = SeaTerritory(self.state, 2, 'English Channel', [])
        paris = InlandTerritory(self.state, 3, 'Paris', 'France', [])

        army = Army(self.state, 0, 'England', picardy)
        fleet = Fleet(self.state, 0, 'France', english_channel)

        self.assertTrue(paris.accessible_by_piece_type(army))
        self.assertFalse(paris.accessible_by_piece_type(fleet))

    def test_sea(self):
        picardy = CoastalTerritory(self.state, 1, 'Picardy', 'France', [], [])
        english_channel = SeaTerritory(self.state, 2, 'English Channel', [])
        irish_sea = SeaTerritory(self.state, 3, 'Irish Sea', [])

        army = Army(self.state, 0, 'England', picardy)
        fleet = Fleet(self.state, 0, 'France', english_channel)

        self.assertFalse(irish_sea.accessible_by_piece_type(army))
        self.assertTrue(irish_sea.accessible_by_piece_type(fleet))


class TestAttackingPieces(TerritoryTestCase):

    def test_attacking_pieces_none(self):
        picardy = CoastalTerritory(self.state, 1, 'Picardy', 'France', [], [])
        self.assertEqual(picardy.attacking_pieces, [])

    def test_attacking_piece_exists(self):
        picardy = CoastalTerritory(self.state, 1, 'Picardy', 'France', [2], [])
        paris = InlandTerritory(self.state, 2, 'Paris', 'France', [1])
        army_paris = Army(self.state, 0, 'France', paris)
        Move(self.state, 0, 'France', paris, picardy)

        self.assertEqual(picardy.attacking_pieces, [army_paris])

    def test_multiple_attacking_piece_exist(self):
        picardy = CoastalTerritory(self.state, 1, 'Picardy', 'France', [2, 3], [])
        paris = InlandTerritory(self.state, 2, 'Paris', 'France', [1])
        brest = CoastalTerritory(self.state, 3, 'Brest', 'France', [1], [])
        army_paris = Army(self.state, 0, 'France', paris)
        fleet_brest = Fleet(self.state, 0, 'France', brest)
        Move(self.state, 0, 'France', paris, picardy)
        Move(self.state, 0, 'France', brest, picardy)

        self.assertEqual(
            set(picardy.attacking_pieces),
            set([army_paris, fleet_brest])
        )

    def test_supporting_piece_not_included(self):
        picardy = CoastalTerritory(self.state, 1, 'Picardy', 'France', [2, 3], [])
        paris = InlandTerritory(self.state, 2, 'Paris', 'France', [1])
        brest = CoastalTerritory(self.state, 3, 'Brest', 'France', [1], [])
        fleet_brest = Fleet(self.state, 0, 'France', brest)
        Support(self.state, 0, 'France', paris, brest, picardy)
        Move(self.state, 0, 'France', brest, picardy)

        self.assertEqual(picardy.attacking_pieces, [fleet_brest])


class TestForeignAttackingPieces(TerritoryTestCase):

    def test_foeign_attacking_pieces(self):
        picardy = CoastalTerritory(self.state, 1, 'Picardy', 'France', [2], [])
        paris = InlandTerritory(self.state, 2, 'Paris', 'France', [1])
        brest = CoastalTerritory(self.state, 3, 'Brest', 'France', [1], [])
        army_paris = Army(self.state, 0, 'England', paris)
        Fleet(self.state, 0, 'France', brest)
        Move(self.state, 0, 'England', paris, picardy)
        Move(self.state, 0, 'France', brest, picardy)

        self.assertEqual(
            picardy.foreign_attacking_pieces('France'),
            [army_paris]
        )


class TestOtherAttackingPieces(TerritoryTestCase):

    def test_other_attacking_pieces(self):
        picardy = CoastalTerritory(self.state, 1, 'Picardy', 'France', [2], [])
        paris = InlandTerritory(self.state, 2, 'Paris', 'France', [1])
        brest = CoastalTerritory(self.state, 3, 'Brest', 'France', [1], [])
        army_paris = Army(self.state, 0, 'England', paris)
        fleet_brest = Fleet(self.state, 0, 'France', brest)
        Move(self.state, 0, 'England', paris, picardy)
        Move(self.state, 0, 'France', brest, picardy)

        self.assertEqual(
            picardy.other_attacking_pieces(fleet_brest),
            [army_paris]
        )


class TestNamedCoasts(TerritoryTestCase):

    def test_named_coast(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [], [])
        spain = CoastalTerritory(self.state, 2, 'Spain', None, [], [])
        spain_north_coast = NamedCoast(self.state, 1, 'North Coast', spain, [])

        self.assertEqual(spain.named_coasts, [spain_north_coast])
        self.assertEqual(london.named_coasts, [])

    def test_is_complex(self):
        london = CoastalTerritory(self.state, 1, 'London', 'England', [], [])
        spain = CoastalTerritory(self.state, 2, 'Spain', None, [], [])
        NamedCoast(self.state, 1, 'North Coast', spain, [])

        self.assertTrue(spain.is_complex)
        self.assertFalse(london.is_complex)
