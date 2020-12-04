from django.test import TestCase
from adjudicator.serializers import GameSerializer


class TestSerializeState(TestCase):

    def setUp(self):
        pass

    def test_serialize_state(self):
        # Shouldn't return named_coast

        # Order shouldn't include type, aux, nation, piece_type, source,
        # target, target_coast, via_convoy

        # Piece shouldn't include type, attacker_territory, nation, territory,
        # retreating

        # Territory shouldn't include type, controlled_by, name, nationality,
        # neighbours, supply_center

        serializer = GameSerializer()
