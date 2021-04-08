from django.test import TestCase
from django.utils import timezone

from core import factories, models, serializers
from core.models.base import OutcomeType, Phase, Season
from core.tests import DiplomacyTestCaseMixin


class BaseSerializerTestCase(TestCase, DiplomacyTestCaseMixin):

    def get_serializer_and_save(self, instance, data):
        serializer = self.serializer_class(instance=instance, data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()


class BaseTurnSerializerTestCase(BaseSerializerTestCase):

    serializer_class = serializers.TurnSerializer

    def setUp(self):
        self.variant = models.Variant.objects.get(id='standard')
        self.user = factories.UserFactory()
        self.england = self.variant.nations.get(name='England')
        self.france = self.variant.nations.get(name='France')
        self.london = self.variant.territories.get(name='london')
        self.paris = self.variant.territories.get(name='paris')
        self.game = models.Game.objects.create(
            name='Test game',
            variant=self.variant,
            num_players=7,
            created_by=self.user,
        )
        self.game.participants.add(self.user)
        self.turn = models.Turn.objects.create(
            game=self.game,
            phase=Phase.ORDER,
            season=Season.SPRING,
            year=1901,
        )
        self.territory_state = self.create_test_territory_state(
            territory=self.london,
            turn=self.turn,
        )
        self.order = self.create_test_order(
            nation=self.england,
            turn=self.turn,
            source=self.london,
        )
        london_piece = self.create_test_piece(game=self.game, nation=self.england)
        self.piece_state = self.create_test_piece_state(
            piece=london_piece,
            territory=self.london,
            turn=self.turn,
        )


class TestPieceStateSerializer(BaseSerializerTestCase):

    serializer_class = serializers.PieceStateSerializer

    def test_create_method_raises_type_error(self):
        serializer = self.serializer_class(data={})
        serializer.is_valid(raise_exception=True)
        with self.assertRaises(TypeError):
            serializer.save()


class TestTerritoryStateSerializer(BaseSerializerTestCase):

    serializer_class = serializers.TerritoryStateSerializer

    def test_create_method_raises_type_error(self):
        serializer = self.serializer_class(data={})
        serializer.is_valid(raise_exception=True)
        with self.assertRaises(TypeError):
            serializer.save()


class TestOrderSerializer(BaseSerializerTestCase):

    serializer_class = serializers.OrderSerializer

    def test_create_method_raises_type_error(self):
        serializer = self.serializer_class(data={})
        serializer.is_valid(raise_exception=True)
        with self.assertRaises(TypeError):
            serializer.save()


class TestNamedCoastSerializer(BaseSerializerTestCase):

    serializer_class = serializers.NamedCoastSerializer

    def test_create_method_raises_type_error(self):
        serializer = self.serializer_class(data={})
        serializer.is_valid(raise_exception=True)
        with self.assertRaises(TypeError):
            serializer.save()

    def test_update_method_raises_type_error(self):
        serializer = self.serializer_class(instance={}, data={})
        serializer.is_valid(raise_exception=True)
        with self.assertRaises(TypeError):
            serializer.save()


class TestDeserializeTurn(BaseTurnSerializerTestCase):

    def setUp(self):
        super().setUp()
        france_piece = self.create_test_piece(game=self.game, nation=self.france)
        self.other_piece_state = self.create_test_piece_state(
            piece=france_piece,
            territory=self.paris,
            turn=self.turn,
        )
        self.data = {
            'orders': [],
            'pieces': [],
            'territories': [],
        }
        self.piece_state_data = {
            'dislodged': False,
            'dislodged_by': None,
            'destroyed': False,
            'destroyed_message': None,
            'id': self.piece_state.id,
        }
        self.other_piece_state_data = {
            'dislodged': False,
            'dislodged_by': None,
            'destroyed': False,
            'destroyed_message': None,
            'id': self.other_piece_state.id,
        }
        self.territory_state_data = {
            'bounce_occurred': False,
            'id': self.territory_state.territory.id,
        }
        self.order_data = {
            'id': self.order.id,
            'illegal': False,
            'illegal_code': None,
            'illegal_verbose': None,
            'outcome': 'succeeds',
        }

    def test_turn_processed(self):
        now = timezone.now()
        instance = self.get_serializer_and_save(self.turn, self.data)
        self.assertTrue(instance.processed)
        self.assertSimilarTimestamp(now, instance.processed_at)

    def test_update_piece_state_sustains(self):
        self.data['pieces'].append(self.piece_state_data)
        self.get_serializer_and_save(self.turn, self.data)
        self.piece_state.refresh_from_db()
        self.assertFalse(self.piece_state.dislodged)
        self.assertIsNone(self.piece_state.dislodged_by)
        self.assertFalse(self.piece_state.destroyed)
        self.assertIsNone(self.piece_state.destroyed_message)

    def test_update_piece_state_dislodged(self):
        self.piece_state_data['dislodged'] = True
        self.piece_state_data['dislodged_by'] = self.other_piece_state.id
        self.data['pieces'].append(self.piece_state_data)
        self.data['pieces'].append(self.other_piece_state_data)
        self.get_serializer_and_save(self.turn, self.data)
        self.piece_state.refresh_from_db()
        self.assertTrue(self.piece_state.dislodged)
        self.assertEqual(self.piece_state.dislodged_by, self.other_piece_state)

    def test_update_piece_state_destroyed(self):
        destroyed_message = 'Destroyed message'
        self.piece_state_data['destroyed'] = True
        self.piece_state_data['destroyed_message'] = destroyed_message
        self.data['pieces'].append(self.piece_state_data)
        self.get_serializer_and_save(self.turn, self.data)
        self.piece_state.refresh_from_db()
        self.assertTrue(self.piece_state.destroyed)
        self.assertEqual(self.piece_state.destroyed_message, destroyed_message)

    def test_update_territory_state(self):
        self.data['territories'].append(self.territory_state_data)
        self.get_serializer_and_save(self.turn, self.data)
        self.territory_state.refresh_from_db()
        self.assertFalse(self.territory_state.bounce_occurred)

    def test_update_territory_state_bounced(self):
        self.territory_state_data['bounce_occurred'] = True
        self.data['territories'].append(self.territory_state_data)
        self.get_serializer_and_save(self.turn, self.data)
        self.territory_state.refresh_from_db()
        self.assertTrue(self.territory_state.bounce_occurred)

    def test_update_order_legal(self):
        self.data['orders'].append(self.order_data)
        self.get_serializer_and_save(self.turn, self.data)
        self.order.refresh_from_db()
        self.assertFalse(self.order.illegal)
        self.assertIsNone(self.order.illegal_code)
        self.assertIsNone(self.order.illegal_verbose)
        self.assertEqual(self.order.outcome, OutcomeType.SUCCEEDS)

    def test_update_order_illegal(self):
        illegal_code = '123'
        illegal_verbose = 'Illegal message'
        self.order_data['illegal'] = True
        self.order_data['illegal_code'] = illegal_code
        self.order_data['illegal_verbose'] = illegal_verbose
        self.order_data['outcome'] = OutcomeType.FAILS
        self.data['orders'].append(self.order_data)
        self.get_serializer_and_save(self.turn, self.data)
        self.order.refresh_from_db()
        self.assertTrue(self.order.illegal)
        self.assertEqual(self.order.illegal_code, illegal_code)
        self.assertEqual(self.order.illegal_verbose, illegal_verbose)
        self.assertEqual(self.order.outcome, OutcomeType.FAILS)

    def test_update_order_build_illegal(self):
        self.order_data['illegal'] = True
        self.order_data['outcome'] = OutcomeType.FAILS
        self.data['orders'].append(self.order_data)
        self.get_serializer_and_save(self.turn, self.data)
        self.order.refresh_from_db()
        self.assertTrue(self.order.illegal)
        self.assertEqual(self.order.outcome, OutcomeType.FAILS)

    def test_deserialize_turn(self):
        data = {
            'orders': [self.order_data],
            'pieces': [self.piece_state_data],
            'territories': [self.territory_state_data]
        }
        self.get_serializer_and_save(self.turn, data)

        self.order.refresh_from_db()
        self.territory_state.refresh_from_db()
        self.piece_state.refresh_from_db()

        self.assertEqual(self.order.outcome, OutcomeType.SUCCEEDS)
        self.assertEqual(self.order.illegal, False)
        self.assertEqual(self.order.illegal_code, None)
        self.assertEqual(self.order.illegal_verbose, None)

        self.assertEqual(self.piece_state.dislodged, False)
        self.assertEqual(self.piece_state.dislodged_by, None)
        self.assertEqual(self.piece_state.destroyed, False)
        self.assertEqual(self.piece_state.destroyed_message, None)

        self.assertEqual(self.territory_state.bounce_occurred, False)
        self.assertEqual(self.territory_state.contested, False)

    def test_deserialize_turn_2(self):
        data = {
            'orders': [
                {
                    'id': self.order.id,
                    'illegal': True,
                    'illegal_code': 'Test',
                    'illegal_verbose': 'Test message',
                    'outcome': 'fails',
                },
            ],
            'pieces': [
                {
                    'dislodged': True,
                    'dislodged_by': self.other_piece_state.id,
                    'destroyed': False,
                    'destroyed_message': None,
                    'id': self.piece_state.id,
                },
                {
                    'dislodged': False,
                    'destroyed': False,
                    'destroyed_message': None,
                    'id': self.other_piece_state.id,
                }
            ],
            'territories': [
                {
                    'bounce_occurred': True,
                    'contested': True,
                    'id': self.territory_state.territory.id,
                }
            ],
        }
        self.get_serializer_and_save(self.turn, data)

        self.order.refresh_from_db()
        self.territory_state.refresh_from_db()
        self.piece_state.refresh_from_db()

        self.assertEqual(self.order.outcome, OutcomeType.FAILS)
        self.assertEqual(self.order.illegal, True)
        self.assertEqual(self.order.illegal_code, 'Test')
        self.assertEqual(self.order.illegal_verbose, 'Test message')

        self.assertEqual(self.piece_state.dislodged, True)
        self.assertEqual(self.piece_state.dislodged_by, self.other_piece_state)
        self.assertEqual(self.piece_state.destroyed, False)
        self.assertEqual(self.piece_state.destroyed_message, None)

        self.assertEqual(self.territory_state.bounce_occurred, True)


class TestSerializeTurn(BaseTurnSerializerTestCase):

    def test_serialize_turn(self):
        models.NamedCoast.objects.create(parent=self.london)
        data = self.serializer_class(self.turn).data
        order_keys = sorted(data['orders'][0].keys())
        expected_order_keys = [
            'aux', 'id', 'nation', 'piece_type', 'source', 'target',
            'target_coast', 'type', 'via_convoy'
        ]
        self.assertEqual(order_keys, expected_order_keys)

        territory_state_keys = sorted(data['territories'][0].keys())
        expected_territory_state_keys = [
            'contested', 'controlled_by', 'id', 'name', 'nationality',
            'neighbours', 'shared_coasts', 'supply_center', 'type'
        ]
        self.assertEqual(expected_territory_state_keys, territory_state_keys)

        piece_state_keys = sorted(data['pieces'][0].keys())

        expected_piece_state_keys = [
            'attacker_territory',
            'id',
            'named_coast',
            'nation',
            'retreating',
            'territory',
            'type'
        ]
        self.assertEqual(expected_piece_state_keys, piece_state_keys)

        named_coast_keys = sorted(data['named_coasts'][0].keys())

        expected_named_coast_keys = [
            'id',
            'name',
            'neighbours',
            'parent',
        ]
        self.assertEqual(expected_named_coast_keys, named_coast_keys)
