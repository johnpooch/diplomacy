from django.test import TestCase

from adjudicator.base import Phase, Season
from adjudicator.nation import Nation
from adjudicator.order import Hold
from adjudicator.piece import Army
from adjudicator.schema import TurnSchema
from adjudicator.territory import CoastalTerritory
from .base import AdjudicatorTestCaseMixin


class TestSerializeTurn(AdjudicatorTestCaseMixin, TestCase):

    def test_serialize_turn(self):
        self.state.next_season = Season.FALL
        self.state.next_phase = Phase.ORDER
        self.state.next_year = 1900
        data = TurnSchema().dump(self.state)
        self.assertEqual(
            sorted(data.keys()),
            ['nations', 'next_phase', 'next_season', 'next_year', 'orders',
             'pieces', 'territories']
        )

    def test_serialize_state_order(self):
        london = CoastalTerritory(self.state, 1, 'London', 1, [2], [])
        Hold(self.state, 1, 1, london)
        data = TurnSchema().dump(self.state)
        order_data = (dict(data['orders'][0]))
        self.assertEqual(
            sorted(order_data.keys()),
            ['id', 'illegal', 'illegal_code', 'illegal_verbose', 'outcome']
        )

    def test_serialize_state_territory(self):
        CoastalTerritory(self.state, 1, 'London', 1, [2], [])
        data = TurnSchema().dump(self.state)
        territory_data = (dict(data['territories'][0]))
        self.assertEqual(
            sorted(territory_data.keys()),
            ['bounce_occurred', 'captured_by', 'id']
        )

    def test_serialize_state_piece(self):
        london = CoastalTerritory(self.state, 1, 'London', 1, [2], [])
        Army(self.state, 1, 1, london)
        data = TurnSchema().dump(self.state)
        piece_data = (dict(data['pieces'][0]))
        self.assertEqual(
            sorted(piece_data.keys()),
            ['destroyed', 'destroyed_message', 'dislodged', 'dislodged_by',
             'dislodged_from', 'id']
        )

    def test_serialize_nation(self):
        Nation(self.state, 1, 'England')
        data = TurnSchema().dump(self.state)
        nation_data = (dict(data['nations'][0]))
        self.assertEqual(
            sorted(nation_data.keys()),
            ['id', 'next_turn_piece_count', 'next_turn_supply_center_count',
             'next_turn_supply_delta']
        )
