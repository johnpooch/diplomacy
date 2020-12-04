from django.test import TestCase

from adjudicator.serializers import GameSerializer
from adjudicator.order import Hold
from adjudicator.piece import Army
from adjudicator.territory import CoastalTerritory
from .base import AdjudicatorTestCaseMixin


class TestSerializeState(AdjudicatorTestCaseMixin, TestCase):

    def test_serialize_state(self):
        # Shouldn't return named_coast

        # Order shouldn't include type, aux, nation, piece_type, source,
        # target, target_coast, via_convoy

        # Piece shouldn't include type, attacker_territory, nation, territory,
        # retreating

        # Territory shouldn't include type, controlled_by, name, nationality,
        # neighbours, supply_center
        serializer = GameSerializer(self.state)
        self.assertEqual(
            sorted(serializer.data.keys()),
            ['orders', 'pieces', 'territories']
        )

    def test_serialize_state_order(self):
        london = CoastalTerritory(self.state, 1, 'London', 1, [2], [])
        Hold(self.state, 1, 1, london)
        serializer = GameSerializer(self.state)
        order_data = (dict(serializer.data['orders'][0]))
        self.assertEqual(
            sorted(order_data.keys()),
            ['id', 'illegal', 'illegal_code', 'illegal_verbose', 'outcome']
        )

    def test_serialize_state_territory(self):
        CoastalTerritory(self.state, 1, 'London', 1, [2], [])
        serializer = GameSerializer(self.state)
        territory_data = (dict(serializer.data['territories'][0]))
        self.assertEqual(
            sorted(territory_data.keys()),
            ['bounce_occurred', 'id']
        )

    def test_serialize_state_piece(self):
        london = CoastalTerritory(self.state, 1, 'London', 1, [2], [])
        Army(self.state, 1, 1, london)
        serializer = GameSerializer(self.state)
        piece_data = (dict(serializer.data['pieces'][0]))
        self.assertEqual(
            sorted(piece_data.keys()),
            ['attacker_territory', 'destroyed', 'destroyed_message',
             'dislodged', 'dislodged_by', 'id']
        )
