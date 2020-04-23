
import unittest
from adjudicator.named_coast import NamedCoast
from adjudicator.order import Move, Support
from adjudicator.state import State
from adjudicator.territory import CoastalTerritory, SeaTerritory, InlandTerritory
from adjudicator.piece import Army, Fleet


class TerritoryTestCase(unittest.TestCase):
    def setUp(self):
        self.state = State()


class TestString(TerritoryTestCase):

    def test_string(self):
        t = CoastalTerritory(1, 'London', 'England', [], [])
        self.assertEqual(str(t), 'London')


class TestNeighbours(TerritoryTestCase):

    def test_neighbours(self):
        london = CoastalTerritory(1, 'London', 'England', [2], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [1], [])
        paris = InlandTerritory(3, 'Paris', 'France', [])
        self.state.register(london, wales, paris)

        self.assertEqual(london.neighbours, {wales})
        self.assertEqual(wales.neighbours, {london})
        self.assertFalse(paris in london.neighbours)


class TestSharedCoasts(TerritoryTestCase):

    def test_shared_coasts(self):
        london = CoastalTerritory(1, 'London', 'England', [2], [2])
        wales = CoastalTerritory(2, 'Wales', 'England', [1], [1])
        paris = InlandTerritory(3, 'Paris', 'France', [])
        self.state.register(london, wales, paris)

        self.assertEqual(london.shared_coasts, {wales})
        self.assertEqual(wales.shared_coasts, {london})
        self.assertFalse(paris in london.neighbours)


class TestAdjacentTo(TerritoryTestCase):

    def test_neighbours(self):
        london = CoastalTerritory(1, 'London', 'England', [2], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [1], [])
        paris = InlandTerritory(3, 'Paris', 'France', [])
        self.state.register(london, wales, paris)

        self.assertTrue(london.adjacent_to(wales))
        self.assertFalse(london.adjacent_to(paris))


class TestPiece(TerritoryTestCase):

    def test_piece(self):
        london = CoastalTerritory(1, 'London', 'England', [], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [], [])
        paris = InlandTerritory(3, 'Paris', 'France', [])
        self.state.register(london, wales, paris)

        army_london = Army(0, 'England', london)
        army_wales = Army(0, 'England', wales)
        self.state.register(army_london, army_wales)

        self.assertEqual(army_london, london.piece)
        self.assertEqual(army_wales, wales.piece)
        self.assertIsNone(paris.piece)


class TestFriendlyPieceExists(TerritoryTestCase):

    def test_friendly_piece_exists(self):
        london = CoastalTerritory(1, 'London', 'England', [], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [], [])
        paris = InlandTerritory(3, 'Paris', 'France', [])
        self.state.register(london, wales, paris)

        army_london = Army(0, 'England', london)
        army_wales = Army(0, 'France', wales)
        self.state.register(army_london, army_wales)

        self.assertTrue(london.friendly_piece_exists('England'))
        self.assertFalse(wales.friendly_piece_exists('England'))
        self.assertFalse(paris.friendly_piece_exists('England'))


class TestOccupied(TerritoryTestCase):

    def test_occupied(self):
        london = CoastalTerritory(1, 'London', 'England', [], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [], [])
        self.state.register(london, wales)

        army_london = Army(0, 'England', london)
        self.state.register(army_london)

        self.assertTrue(london.occupied)
        self.assertFalse(wales.occupied)


class TestOccupiedBy(TerritoryTestCase):

    def test_occupied_by(self):
        london = CoastalTerritory(1, 'London', 'England', [], [])
        wales = CoastalTerritory(2, 'Wales', 'England', [], [])
        paris = InlandTerritory(3, 'Paris', 'England', [])
        self.state.register(london, wales, paris)

        army_london = Army(0, 'England', london)
        army_paris = Army(0, 'France', paris)
        self.state.register(army_london, army_paris)

        self.assertTrue(london.occupied_by('England'))
        self.assertFalse(wales.occupied_by('England'))
        self.assertFalse(paris.occupied_by('England'))


class TestAccessibleByPieceType(TerritoryTestCase):

    def test_coastal(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [], [])
        english_channel = SeaTerritory(2, 'English Channel', [])
        brest = CoastalTerritory(3, 'Brest', 'France', [], [])
        self.state.register(picardy, english_channel, brest)

        army = Army(0, 'England', picardy)
        fleet = Fleet(0, 'France', english_channel)
        self.state.register(army, fleet)

        self.assertTrue(brest.accessible_by_piece_type(army))
        self.assertTrue(brest.accessible_by_piece_type(fleet))

    def test_inland(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [], [])
        english_channel = SeaTerritory(2, 'English Channel', [])
        paris = InlandTerritory(3, 'Paris', 'France', [])
        self.state.register(picardy, english_channel, paris)

        army = Army(0, 'England', picardy)
        fleet = Fleet(0, 'France', english_channel)
        self.state.register(army, fleet)

        self.assertTrue(paris.accessible_by_piece_type(army))
        self.assertFalse(paris.accessible_by_piece_type(fleet))

    def test_sea(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [], [])
        english_channel = SeaTerritory(2, 'English Channel', [])
        irish_sea = SeaTerritory(3, 'Irish Sea', [])
        self.state.register(picardy, english_channel, irish_sea)

        army = Army(0, 'England', picardy)
        fleet = Fleet(0, 'France', english_channel)
        self.state.register(army, fleet)

        self.assertFalse(irish_sea.accessible_by_piece_type(army))
        self.assertTrue(irish_sea.accessible_by_piece_type(fleet))


class TestAttackingPieces(TerritoryTestCase):

    def test_attacking_pieces_none(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [], [])
        self.state.register(picardy)
        self.assertEqual(picardy.attacking_pieces, set())

    def test_attacking_piece_exists(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [2], [])
        paris = InlandTerritory(2, 'Paris', 'France', [1])
        army_paris = Army(0, 'France', paris)
        move = Move(0, 'France', paris, picardy)
        self.state.register(picardy, paris, army_paris, move)

        self.assertEqual(picardy.attacking_pieces, {army_paris})

    def test_multiple_attacking_piece_exist(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [2, 3], [])
        paris = InlandTerritory(2, 'Paris', 'France', [1])
        brest = CoastalTerritory(3, 'Brest', 'France', [1], [])
        army_paris = Army(0, 'France', paris)
        fleet_brest = Fleet(0, 'France', brest)
        move_1 = Move(0, 'France', paris, picardy)
        move_2 = Move(0, 'France', brest, picardy)
        self.state.register(picardy, paris, brest, army_paris, fleet_brest,
                            move_1, move_2)

        self.assertEqual(picardy.attacking_pieces, {army_paris, fleet_brest})

    def test_supporting_piece_not_included(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [2, 3], [])
        paris = InlandTerritory(2, 'Paris', 'France', [1])
        brest = CoastalTerritory(3, 'Brest', 'France', [1], [])
        fleet_brest = Fleet(0, 'France', brest)
        support = Support(0, 'France', paris, brest, picardy)
        move = Move(0, 'France', brest, picardy)
        self.state.register(picardy, paris, brest, fleet_brest, move, support)

        self.assertEqual(picardy.attacking_pieces, {fleet_brest})


class TestForeignAttackingPieces(TerritoryTestCase):

    def test_foeign_attacking_pieces(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [2], [])
        paris = InlandTerritory(2, 'Paris', 'France', [1])
        brest = CoastalTerritory(3, 'Brest', 'France', [1], [])
        army_paris = Army(0, 'England', paris)
        fleet_brest = Fleet(0, 'France', brest)
        move_1 = Move(0, 'England', paris, picardy)
        move_2 = Move(0, 'France', brest, picardy)
        self.state.register(picardy, paris, brest, army_paris, fleet_brest, move_1, move_2)

        self.assertEqual(
            picardy.foreign_attacking_pieces('France'),
            [army_paris]
        )


class TestOtherAttackingPieces(TerritoryTestCase):

    def test_other_attacking_pieces(self):
        picardy = CoastalTerritory(1, 'Picardy', 'France', [2], [])
        paris = InlandTerritory(2, 'Paris', 'France', [1])
        brest = CoastalTerritory(3, 'Brest', 'France', [1], [])
        army_paris = Army(0, 'England', paris)
        fleet_brest = Fleet(0, 'France', brest)
        move_1 = Move(0, 'England', paris, picardy)
        move_2 = Move(0, 'France', brest, picardy)
        self.state.register(picardy, paris, brest, army_paris, fleet_brest, move_1, move_2)

        self.assertEqual(
            picardy.other_attacking_pieces(fleet_brest),
            [army_paris]
        )


class TestNamedCoasts(TerritoryTestCase):

    def test_named_coast(self):
        london = CoastalTerritory(1, 'London', 'England', [], [])
        spain = CoastalTerritory(2, 'Spain', None, [], [])
        spain_north_coast = NamedCoast(1, 'North Coast', spain, [])
        self.state.register(london, spain, spain_north_coast)

        self.assertEqual(spain.named_coasts, {spain_north_coast})
        self.assertEqual(london.named_coasts, set())

    def test_is_complex(self):
        london = CoastalTerritory(1, 'London', 'England', [], [])
        spain = CoastalTerritory(2, 'Spain', None, [], [])
        spain_north_coast = NamedCoast(1, 'North Coast', spain, [])
        self.state.register(london, spain, spain_north_coast)

        self.assertTrue(spain.is_complex)
        self.assertFalse(london.is_complex)
