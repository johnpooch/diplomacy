from django.test import TestCase

from service import serializers
from core.tests import DiplomacyTestCaseMixin
from core.models.base import GameStatus


class TesNationStateOrdersStatusSerializer(TestCase, DiplomacyTestCaseMixin):

    expected_num_queries = 4
    serializer_class = serializers.NationStateOrdersStatusSerializer

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(
            variant=self.variant,
            status=GameStatus.ACTIVE,
        )
        self.nation = self.create_test_nation(variant=self.variant)
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()
        self.nation_state = self.create_test_nation_state(
            nation=self.nation,
            turn=self.turn,
            user=self.user,
        )

    def serialize_object(self, obj):
        return self.serializer_class(obj).data

    def test_nation_state(self):
        with self.assertNumQueries(self.expected_num_queries):
            data = self.serialize_object(self.nation_state)
        self.assertEqual(data['id'], self.nation_state.id)
        self.assertEqual(data['num_orders'], self.nation_state.num_orders)
        self.assertEqual(data['num_supply_centers'], self.nation_state.num_supply_centers)
        self.assertEqual(data['supply_delta'], self.nation_state.supply_delta)
        self.assertEqual(data['num_builds'], self.nation_state.num_builds)
        self.assertEqual(data['num_disbands'], self.nation_state.num_disbands)
