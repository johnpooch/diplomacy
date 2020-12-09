import unittest

from adjudicator.decisions import Outcomes
from adjudicator.nation import Nation
from adjudicator.order import Disband, Hold
from adjudicator.piece import Army
from adjudicator.territory import InlandTerritory

from .base import AdjudicatorTestCaseMixin


class NationTestCase(AdjudicatorTestCaseMixin, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.nation = Nation(self.state, 1, 'England')
        self.other_nation = Nation(self.state, 2, 'France')


class TestPieces(NationTestCase):

    def test_pieces_none(self):
        self.assertEqual(self.nation.pieces, [])

    def test_pieces_not_belonging_to_nation(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [])
        Army(self.state, 1, 2, territory)
        self.assertEqual(self.nation.pieces, [])

    def test_pieces(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [])
        army = Army(self.state, 1, self.nation.id, territory)
        self.assertEqual(self.nation.pieces, [army])


class TestControlledTerritores(NationTestCase):

    def test_controlled_territores_none(self):
        self.assertEqual(self.nation.controlled_territories, [])

    def test_controlled_territories(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [], controlled_by=self.nation.id)
        self.assertEqual(self.nation.controlled_territories, [territory])

    def test_controlled_includes_captured_by_other(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [], controlled_by=self.nation.id)
        territory.captured_by = self.other_nation.id
        self.assertEqual(self.nation.controlled_territories, [territory])


class TestCapturedTerritories(NationTestCase):

    def test_captured_territores_none(self):
        self.assertEqual(self.nation.captured_territories, [])

    def test_captured_includes_controlled_by_other(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [], controlled_by=self.other_nation.id)
        territory.captured_by = self.nation.id
        self.assertEqual(self.nation.captured_territories, [territory])


class TestNextTurnPieceCount(NationTestCase):

    def test_next_turn_piece_count_no_pieces(self):
        self.assertEqual(self.nation.next_turn_piece_count, 0)

    def test_next_turn_piece_count_destroyed(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [])
        army = Army(self.state, 1, self.nation.id, territory)
        army.destroyed = True
        self.assertEqual(self.nation.next_turn_piece_count, 0)

    def test_next_turn_piece_count_successful_disband(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [])
        Army(self.state, 1, self.nation.id, territory)
        disband = Disband(self.state, 1, self.nation.id, territory)
        disband.outcome = Outcomes.SUCCEEDS
        self.assertEqual(self.nation.next_turn_piece_count, 0)

    def test_next_turn_piece_count_successful_hold(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [])
        Army(self.state, 1, self.nation.id, territory)
        Hold(self.state, 1, self.nation.id, territory)
        self.assertEqual(self.nation.next_turn_piece_count, 1)

    def test_next_turn_piece_count(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [])
        Army(self.state, 1, self.nation.id, territory)
        self.assertEqual(self.nation.next_turn_piece_count, 1)


class TestNextTurnSupplyCenterCount(NationTestCase):

    def test_does_not_include_no_supply_center_controlled(self):
        InlandTerritory(self.state, 1, 'Paris', 2, [], controlled_by=self.nation.id)
        self.assertEqual(self.nation.next_turn_supply_center_count, 0)

    def test_does_not_include_no_supply_center_captured(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [])
        territory.captured_by = self.nation.id
        self.assertEqual(self.nation.next_turn_supply_center_count, 0)

    def test_next_turn_supply_center_count_captured_by_other(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [], True, controlled_by=self.nation.id)
        territory.captured_by = self.other_nation.id
        self.assertEqual(self.nation.next_turn_supply_center_count, 0)

    def test_next_turn_supply_center_count_captured_from_other(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [], True, controlled_by=self.other_nation.id)
        territory.captured_by = self.nation.id
        self.assertEqual(self.nation.next_turn_supply_center_count, 1)

    def test_next_turn_supply_center_count_controlled(self):
        InlandTerritory(self.state, 1, 'Paris', 2, [], True, controlled_by=self.nation.id)
        self.assertEqual(self.nation.next_turn_supply_center_count, 1)


class TestNextTurnSupplyDelta(NationTestCase):

    def test_next_turn_supply_delta(self):
        territory = InlandTerritory(self.state, 1, 'Paris', 2, [], True, controlled_by=self.nation.id)
        army = Army(self.state, 1, self.nation.id, territory)
        self.assertEqual(self.nation.next_turn_supply_delta, 0)
        army.destroyed = True
        self.assertEqual(self.nation.next_turn_supply_delta, 1)
