from unittest import mock
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core import factories, models
from core.tests import DiplomacyTestCaseMixin
from core.models.base import (
    DrawStatus, DrawResponse, GameStatus, OrderType, Phase, PieceType, Season,
    SurrenderStatus
)
from service import validators


serializer_process_turn_path = 'service.serializers.process_turn'


def set_processed(self, processed_at=None):
    self.processed = True
    self.processed_at = processed_at or timezone.now()
    self.save()


class TestGetGames(APITestCase):

    max_diff = None

    def setUp(self):
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

    def test_get_all_games_unauthenticated(self):
        """
        Cannot get all games if not authenticated.
        """
        self.client.logout()
        url = reverse('list-games')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestGetCreateGame(APITestCase):

    def test_get_create_game(self):
        """
        Get create game returns a form.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

        url = reverse('create-game')
        response = self.client.get(url, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_get_create_game_unauthenticated(self):
        """
        Cannot get create game when unauthenticated.
        """
        url = reverse('create-game')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestCreateGame(APITestCase):

    def test_post_invalid_game(self):
        """
        Posting invalid game data causes a 400 error.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)

        data = {}
        url = reverse('create-game')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_post_valid_game(self):
        """
        Posting valid game data creates a game instance and redirects to
        `user-games` view. The user is automatically added as a participant of
        the game.
        """
        user = factories.UserFactory()
        self.client.force_authenticate(user=user)
        variant = models.Variant.objects.get(identifier='standard')

        data = {
            'name': 'Test Game',
        }
        url = reverse('create-game')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            models.Game.objects.get(
                name='Test Game',
                created_by=user,
                variant=variant,
                participants=user,
            )
        )

    def test_post_unauthorized(self):
        """
        Cannot post when unauthorized.
        """
        url = reverse('create-game')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestJoinGame(APITestCase):

    def setUp(self):
        self.data = {}
        self.user = factories.UserFactory()
        self.variant = models.Variant.objects.get(identifier='standard')
        self.game = models.Game.objects.create(
            status=GameStatus.PENDING,
            variant=self.variant,
            name='Test Game',
            created_by=self.user,
            num_players=7
        )
        self.url = reverse('toggle-join-game', args=[self.game.slug])

    def test_join_game_unauthorized(self):
        """
        Cannot join a game when unauthorized.
        """
        response = self.client.patch(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_join_game_full(self):
        """
        Cannot join a game when the game already has enough participants.
        """
        joined_user = factories.UserFactory()
        self.game.num_players = 1
        self.game.participants.add(joined_user)
        self.game.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_join_game_ended(self):
        """
        Cannot join a game when the game already has ended.
        """
        self.game.status = GameStatus.ENDED
        self.game.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_join_game_success(self):

        self.game.status = GameStatus.PENDING
        self.game.save()
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user in self.game.participants.all())

    @patch('core.models.Game.initialize')
    def test_join_game_initialise_game(self, mock_initialize):
        self.game.num_players = 1
        self.game.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_initialize.assert_called()


class TestGetGameState(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.client.force_authenticate(user=self.user)
        self.variant = models.Variant.objects.create(name='test')
        self.game = models.Game.objects.create(
            variant=self.variant,
            name='Test game',
            status=GameStatus.ACTIVE,
            num_players=1,
            created_by=self.user,
        )
        self.turn = models.Turn.objects.create(
            game=self.game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        self.nation = models.Nation.objects.create(
            variant=self.variant,
            name='Test Nation',
        )
        self.nation_state = models.NationState.objects.create(
            nation=self.nation,
            turn=self.turn,
            user=self.user,
        )
        self.territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        self.territory_state = models.TerritoryState.objects.create(
            territory=self.territory,
            turn=self.turn,
            controlled_by=self.nation_state.nation,
        )
        self.territory = self.territory_state.territory
        self.piece = models.Piece.objects.create(
            game=self.game,
            nation=self.nation_state.nation,
            type=PieceType.ARMY,
        )
        self.piece_state = models.PieceState.objects.create(
            turn=self.turn,
            piece=self.piece,
            territory=self.territory,
        )
        self.url = reverse('game-state', args=[self.game.slug])

    def test_get_game_state_unauthorized(self):
        self.client.logout()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_game_state_live_game(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_game_state_pending_game(self):
        self.game.status = GameStatus.PENDING
        self.game.save()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_game_state_ended_game(self):
        self.game.status = GameStatus.ENDED
        self.game.save()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_game_state_current_turn_orders_hidden(self):
        models.Order.objects.create(
            turn=self.turn,
            source=self.territory,
            nation=self.nation
        )
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['turns'][0]['orders'])


class TestListOrders(APITestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.client.force_authenticate(user=self.user)

        self.variant = factories.VariantFactory()
        self.game = models.Game.objects.create(
            status=GameStatus.ACTIVE,
            variant=self.variant,
            name='Test Game',
            created_by=self.user,
            num_players=7
        )
        self.game.participants.add(self.user)
        self.turn = models.Turn.objects.create(
            game=self.game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        self.nation = models.Nation.objects.create(
            variant=self.variant,
            name='Test Nation',
        )
        self.nation_state = models.NationState.objects.create(
            nation=self.nation,
            turn=self.turn,
            user=self.user,
        )
        self.territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        self.territory_state = models.TerritoryState.objects.create(
            territory=self.territory,
            turn=self.turn,
            controlled_by=self.nation_state.nation,
        )
        self.territory = self.territory_state.territory
        self.piece = models.Piece.objects.create(
            game=self.game,
            nation=self.nation_state.nation,
            type=PieceType.ARMY,
        )
        self.piece_state = models.PieceState.objects.create(
            turn=self.turn,
            piece=self.piece,
            territory=self.territory,
        )
        self.url = reverse('orders', args=[self.turn.id])

    def test_no_orders(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(response.data, [])

    def test_orders(self):
        models.Order.objects.create(
            turn=self.turn,
            source=self.territory,
            nation=self.nation
        )
        response = self.client.get(self.url, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nation'], self.nation.id)

    def test_other_user_orders(self):
        other_user = factories.UserFactory()
        other_nation = models.Nation.objects.create(
            variant=self.variant,
            name='Other Nation',
        )
        models.NationState.objects.create(
            nation=self.nation,
            turn=self.turn,
            user=other_user,
        )
        models.Order.objects.create(
            turn=self.turn,
            source=self.territory,
            nation=self.nation
        )
        models.Order.objects.create(
            turn=self.turn,
            source=self.territory,
            nation=other_nation
        )
        response = self.client.get(self.url, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nation'], self.nation.id)


class TestCreateOrder(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.client.force_authenticate(user=self.user)

        self.variant = factories.VariantFactory()
        self.game = models.Game.objects.create(
            status=GameStatus.ACTIVE,
            variant=self.variant,
            name='Test Game',
            created_by=self.user,
            num_players=7
        )
        self.game.participants.add(self.user)
        self.turn = models.Turn.objects.create(
            game=self.game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        self.nation = models.Nation.objects.create(
            variant=self.variant,
            name='Test Nation',
        )
        self.nation_state = models.NationState.objects.create(
            nation=self.nation,
            turn=self.turn,
            user=self.user,
        )
        self.territory = models.Territory.objects.create(
            variant=self.variant,
            name='Paris',
            nationality=self.nation,
            supply_center=True,
        )
        self.territory_state = models.TerritoryState.objects.create(
            territory=self.territory,
            turn=self.turn,
            controlled_by=self.nation_state.nation,
        )
        self.territory = self.territory_state.territory
        self.piece = models.Piece.objects.create(
            game=self.game,
            nation=self.nation_state.nation,
            type=PieceType.ARMY,
        )
        self.piece_state = models.PieceState.objects.create(
            turn=self.turn,
            piece=self.piece,
            territory=self.territory,
        )
        self.data = {
            'source': self.territory.id,
        }
        self.url = reverse('order', args=[self.game.slug])

    def test_get(self):
        response = self.client.get(self.url, self.data, format='json')
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_create_order_unauthorized(self):
        self.client.logout()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_not_participant(self):
        self.game.participants.remove(self.user)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_game_pending(self):
        self.game.status = GameStatus.PENDING
        self.game.save()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_game_ended(self):
        self.game.status = GameStatus.ENDED
        self.game.save()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_no_orders_left_retreat_and_disband(self):
        models.Turn.objects.create(
            game=self.game,
            season=Season.SPRING,
            phase=Phase.RETREAT_AND_DISBAND,
            year=1900,
            current_turn=True,
        )
        nation_state = factories.NationStateFactory(
            turn=self.game.get_current_turn(),
            user=self.user,
        )
        territory_state = factories.TerritoryStateFactory(
            turn=self.game.get_current_turn(),
            controlled_by=nation_state.nation,
        )
        models.PieceState.objects.all().delete()
        territory = territory_state.territory
        self.data = {
            'source': self.territory.id,
            'target': territory.id,
            'type': OrderType.RETREAT,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_valid(self):

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.Order.objects.get())  # object created

    def test_create_order_valid_over_writes(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.Order.objects.get())  # object created

        territory_state = factories.TerritoryStateFactory(
            turn=self.turn,
            controlled_by=self.nation_state.nation,
        )
        territory = territory_state.territory
        self.data = {
            'source': self.territory.id,
            'target': territory.id,
            'type': OrderType.MOVE,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = models.Order.objects.get()
        self.assertEqual(order.type, OrderType.MOVE)
        self.assertEqual(order.target, territory)

    def test_create_order_hold_during_retreat(self):
        models.Turn.objects.create(
            game=self.game,
            season=Season.SPRING,
            phase=Phase.RETREAT_AND_DISBAND,
            year=1900,
            current_turn=True,
        )
        nation_state = factories.NationStateFactory(
            turn=self.game.get_current_turn(),
            user=self.user,
        )
        territory_state = factories.TerritoryStateFactory(
            turn=self.game.get_current_turn(),
            controlled_by=nation_state.nation,
        )
        self.territory = territory_state.territory
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_retreat_for_must_retreat_piece(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.SPRING,
            phase=Phase.RETREAT_AND_DISBAND,
            year=1900,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        territory_state = factories.TerritoryStateFactory(
            turn=turn,
            controlled_by=self.nation_state.nation,
        )
        self.piece_state.turn = turn
        self.piece_state.must_retreat = True
        self.piece_state.save()
        territory = territory_state.territory
        self.data = {
            'source': self.territory.id,
            'target': territory.id,
            'type': OrderType.RETREAT,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_retreat_for_non_must_retreat_piece(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.SPRING,
            phase=Phase.RETREAT_AND_DISBAND,
            year=1900,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        territory_state = factories.TerritoryStateFactory(
            turn=turn,
            controlled_by=self.nation_state.nation,
        )
        self.piece_state.turn = turn
        self.piece_state.save()
        territory = territory_state.territory
        self.data = {
            'source': self.territory.id,
            'target': territory.id,
            'type': OrderType.RETREAT,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_build_during_order(self):
        self.data['type'] = OrderType.BUILD
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_build_valid(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.territory_state.turn = turn
        self.territory_state.save()
        models.Piece.objects.all().delete()
        models.PieceState.objects.all().delete()
        self.data = {
            'source': self.territory.id,
            'type': OrderType.BUILD,
            'piece_type': PieceType.ARMY,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_build_no_builds(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        models.Piece.objects.all().delete()
        models.PieceState.objects.all().delete()
        self.data = {
            'source': self.territory.id,
            'type': OrderType.BUILD,
            'piece_type': PieceType.ARMY,
        }
        self.assertEqual(self.nation_state.supply_delta, 0)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_build_with_disbands(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.piece_state.turn = turn
        self.piece_state.save()
        self.data = {
            'source': self.territory.id,
            'type': OrderType.BUILD,
            'piece_type': PieceType.ARMY,
        }
        self.assertEqual(self.nation_state.supply_delta, -1)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_disband_valid(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.territory_state.turn = turn
        self.territory_state.territory.supply_center = False
        self.territory_state.territory.save()
        self.territory_state.save()
        self.piece_state.turn = turn
        self.piece_state.save()
        self.data = {
            'source': self.piece_state.territory.id,
            'type': OrderType.DISBAND,
        }
        self.assertEqual(self.nation_state.supply_delta, -1)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_disband_no_disbands(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.territory_state.turn = turn
        self.territory_state.territory.save()
        self.territory_state.save()
        self.piece_state.turn = turn
        self.piece_state.save()
        self.data = {
            'source': self.piece_state.territory.id,
            'type': OrderType.DISBAND,
        }
        self.assertEqual(self.nation_state.supply_delta, 0)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_too_many_disbands(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        territory = models.Territory.objects.create(
            variant=self.variant,
            nationality=self.nation,
            name='Picardy',
        )
        models.TerritoryState.objects.create(
            territory=territory,
            turn=turn,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.territory_state.turn = turn
        self.territory_state.territory.supply_center = False
        self.territory_state.territory.save()
        self.territory_state.save()
        self.piece_state.turn = turn
        self.piece_state.save()
        self.assertEqual(self.nation_state.supply_delta, -1)
        self.assertEqual(self.nation_state.num_orders_remaining, 1)
        data = {
            'source': self.piece_state.territory.id,
            'type': OrderType.DISBAND,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.nation_state.num_orders_remaining, 0)
        data = {
            'source': territory.id,
            'type': OrderType.DISBAND,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_build_occupied_territory(self):
        turn = models.Turn.objects.create(
            game=self.game,
            season=Season.FALL,
            phase=Phase.BUILD,
            year=1901,
            current_turn=True,
        )
        self.nation_state.turn = turn
        self.nation_state.save()
        self.territory_state.turn = turn
        self.territory_state.save()
        models.PieceState.objects.create(
            piece=self.piece,
            turn=turn,
            territory=self.territory,
        )
        territory = models.Territory.objects.create(
            variant=self.variant,
            nationality=self.nation,
            name='Picardy',
            supply_center=True,
        )
        models.TerritoryState.objects.create(
            territory=territory,
            controlled_by=self.nation,
            turn=turn,
        )
        self.data = {
            'source': self.territory.id,
            'type': OrderType.BUILD,
            'piece_type': PieceType.ARMY,
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestFinalizeOrders(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.variant = factories.VariantFactory()
        self.game = models.Game.objects.create(
            status=GameStatus.ACTIVE,
            variant=self.variant,
            name='Test Game',
            created_by=self.user,
            num_players=7
        )
        self.game.participants.add(self.user)
        turn = models.Turn.objects.create(
            game=self.game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        nation = models.Nation.objects.create(
            variant=self.game.variant,
            name='France',
        )
        self.nation_state = models.NationState.objects.create(
            nation=nation,
            turn=turn,
            user=self.user,
        )
        territory_state = factories.TerritoryStateFactory(
            turn=turn,
            controlled_by=self.nation_state.nation,
        )
        self.territory = territory_state.territory
        self.url = reverse(
            'toggle-finalize-orders',
            args=[self.nation_state.id]
        )
        self.data = {}

    def test_finalize_when_not_participant(self):
        self.game.participants.all().delete()
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_finalize_when_game_not_active(self):
        self.client.force_authenticate(user=self.user)
        self.game.status = GameStatus.PENDING
        self.game.save()
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_finalize_orders_with_no_orders(self):
        self.client.force_authenticate(user=self.user)
        with mock.patch(serializer_process_turn_path, set_processed):
            response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nation_state.refresh_from_db()
        self.assertTrue(self.nation_state.orders_finalized)

    def test_can_finalize_orders_with_orders(self):
        self.client.force_authenticate(user=self.user)
        models.Order.objects.create(
            turn=self.game.get_current_turn(),
            nation=self.nation_state.nation,
            source=self.territory
        )
        with mock.patch(serializer_process_turn_path, set_processed):
            response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nation_state.refresh_from_db()
        self.assertTrue(self.nation_state.orders_finalized)

    def test_once_all_orders_finalized_turn_advances(self):
        self.client.force_authenticate(user=self.user)
        turn = self.game.get_current_turn()
        turn.nationstates.set([self.nation_state])
        with mock.patch(serializer_process_turn_path, set_processed):
            response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nation_state.refresh_from_db()
        self.assertTrue(self.nation_state.orders_finalized)


class TestUnfinalizeOrders(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory()
        self.variant = factories.VariantFactory()
        self.game = models.Game.objects.create(
            status=GameStatus.ACTIVE,
            variant=self.variant,
            name='Test Game',
            created_by=self.user,
            num_players=7
        )
        self.game.participants.add(self.user)
        turn = models.Turn.objects.create(
            game=self.game,
            year=1901,
            phase=Phase.ORDER,
            season=Season.SPRING,
        )
        nation = models.Nation.objects.create(
            variant=self.game.variant,
            name='France',
        )
        self.nation_state = models.NationState.objects.create(
            nation=nation,
            turn=turn,
            user=self.user,
            orders_finalized=True,
        )
        territory_state = factories.TerritoryStateFactory(
            turn=self.game.get_current_turn(),
            controlled_by=self.nation_state.nation,
        )
        self.territory = territory_state.territory
        self.url = reverse(
            'toggle-finalize-orders',
            args=[self.nation_state.id]
        )
        self.data = {}

    @patch('core.models.Turn.ready_to_process', False)
    def test_unfinalize_when_not_participant(self):
        self.game.participants.all().delete()
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('core.models.Turn.ready_to_process', False)
    def test_unfinalize_when_game_not_active(self):
        self.client.force_authenticate(user=self.user)
        self.game.status = GameStatus.PENDING
        self.game.save()
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('core.models.Turn.ready_to_process', False)
    def test_can_unfinalize_orders_with_no_orders(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nation_state.refresh_from_db()
        self.assertFalse(self.nation_state.orders_finalized)

    @patch('core.models.Turn.ready_to_process', False)
    def test_can_unfinalize_orders_with_orders(self):
        self.client.force_authenticate(user=self.user)
        models.Order.objects.create(
            turn=self.game.get_current_turn(),
            nation=self.nation_state.nation,
            source=self.territory
        )
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.nation_state.refresh_from_db()
        self.assertFalse(self.nation_state.orders_finalized)


class TestSurrender(APITestCase, DiplomacyTestCaseMixin):

    view_name = 'surrender'

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(
            variant=self.variant,
            status=GameStatus.ACTIVE,
        )
        self.nation = self.create_test_nation(variant=self.variant)
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()
        self.game.participants.add(self.user)
        self.nation_state = self.create_test_nation_state(
            nation=self.nation,
            turn=self.turn,
            user=self.user,
        )
        self.url = reverse(self.view_name, args=[self.turn.id])
        self.data = {}

    def test_surrender_when_not_participant(self):
        self.game.participants.all().delete()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_surrender_when_game_not_active(self):
        self.client.force_authenticate(user=self.user)
        self.game.status = GameStatus.PENDING
        self.game.save()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_surrender(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        models.Surrender.objects.get(
            user=self.nation_state.user,
            nation_state=self.nation_state,
            status=SurrenderStatus.PENDING,
        )


class TestCancelSurrender(APITestCase, DiplomacyTestCaseMixin):

    view_name = 'cancel-surrender'

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(
            variant=self.variant,
            status=GameStatus.ACTIVE,
        )
        self.nation = self.create_test_nation(variant=self.variant)
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()
        self.game.participants.add(self.user)
        self.nation_state = self.create_test_nation_state(
            nation=self.nation,
            turn=self.turn,
            user=self.user,
        )
        self.surrender = models.Surrender.objects.create(
            user=self.nation_state.user,
            nation_state=self.nation_state,
            status=SurrenderStatus.PENDING,
        )
        self.url = reverse(
            self.view_name,
            args=[self.turn.id, self.surrender.id]
        )
        self.data = {}

    def test_cancel_surrender(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        models.Surrender.objects.get(
            user=self.nation_state.user,
            nation_state=self.nation_state,
            status=SurrenderStatus.CANCELED,
        )


class TestProposeDraw(APITestCase, DiplomacyTestCaseMixin):

    view_name = 'propose-draw'

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(
            variant=self.variant,
            status=GameStatus.ACTIVE,
        )
        self.england = self.create_test_nation(
            variant=self.variant,
            name='England'
        )
        self.france = self.create_test_nation(
            variant=self.variant,
            name='France'
        )
        self.germany = self.create_test_nation(
            variant=self.variant,
            name='Germany'
        )
        self.italy = self.create_test_nation(
            variant=self.variant,
            name='Italy'
        )
        self.austria = self.create_test_nation(
            variant=self.variant,
            name='Austria-Hungary',
        )
        self.turkey = self.create_test_nation(
            variant=self.variant,
            name='Turkey',
        )
        self.russia = self.create_test_nation(
            variant=self.variant,
            name='Russia',
        )
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()
        self.game.participants.add(self.user)
        self.nation_state = self.create_test_nation_state(
            nation=self.england,
            turn=self.turn,
            user=self.user,
        )
        self.url = reverse(self.view_name, args=[self.turn.id])
        self.client.force_authenticate(user=self.user)

    def test_proposing_player_surrendering(self):
        data = {
            'nations': [self.france.id, self.germany.id, self.italy.id]
        }
        self.surrender = models.Surrender.objects.create(
            user=self.user,
            nation_state=self.nation_state,
            status=SurrenderStatus.PENDING,
        )
        response = self.client.post(self.url, data, format='json')
        error = response.data['non_field_errors'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(error),
            validators.NotSurrenderingValidator.message
        )

    def test_not_current_turn(self):
        self.turn.current_turn = False
        self.turn.save()
        data = {
            'nations': [self.france.id, self.germany.id, self.italy.id]
        }
        response = self.client.post(self.url, data, format='json')
        error = response.data['turn'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(error), validators.CurrentTurnValidator.message)

    def test_game_not_active(self):
        self.game.status = GameStatus.ENDED
        self.game.save()
        data = {
            'nations': [self.france.id, self.germany.id, self.italy.id]
        }
        response = self.client.post(self.url, data, format='json')
        error = response.data['turn'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(error), validators.CurrentTurnValidator.message)

    def test_nations_not_in_variant(self):
        other_variant = self.create_test_variant(name='Other variant')
        other_variant_nation = self.create_test_nation(variant=other_variant)
        data = {
            'nations': [other_variant_nation.id, self.germany.id]
        }
        response = self.client.post(self.url, data, format='json')
        error = response.data['non_field_errors'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(error),
            validators.NationsInVariantValidator.message
        )

    def test_nations_not_in_civil_disorder(self):
        self.germany.user = None
        self.germany.save()
        data = {'nations': [self.germany.id]}
        models.NationState.objects.create(turn=self.turn, nation=self.germany)
        response = self.client.post(self.url, data, format='json')
        error = response.data['non_field_errors'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(error), validators.NationsActiveValidator.message)

    def test_already_proposed_draw(self):
        self.create_test_draw(
            turn=self.turn,
            proposed_by=self.england,
            proposed_by_user=self.user,
        )
        data = {'nations': [self.germany.id]}
        response = self.client.post(self.url, data, format='json')
        error = response.data['non_field_errors'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(error),
            validators.OneProposedDrawValidator.message,
        )

    def test_proposed_players_not_enough_strength(self):
        data = {'nations': [self.germany.id]}
        self.create_test_nation_state(turn=self.turn, nation=self.germany)
        self.create_test_nation_state(turn=self.turn, nation=self.england)
        response = self.client.post(self.url, data, format='json')
        error = response.data['non_field_errors'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(error),
            (
                validators.ProposedDrawStrengthValidator.message
                % self.variant.num_supply_centers_to_win
            ),
        )

    @patch('service.validators.get_combined_strength')
    def test_too_many_nations(self, mock_get_combined_strength):
        data = {
            'nations': [
                self.france.id, self.germany.id, self.italy.id, self.russia.id
            ]
        }
        mock_get_combined_strength.return_value = 20
        self.create_test_nation_state(turn=self.turn, nation=self.england)
        self.create_test_nation_state(turn=self.turn, nation=self.france)
        self.create_test_nation_state(turn=self.turn, nation=self.germany)
        self.create_test_nation_state(turn=self.turn, nation=self.italy)
        self.create_test_nation_state(turn=self.turn, nation=self.russia)

        response = self.client.post(self.url, data, format='json')
        error = response.data['non_field_errors'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(error),
            (
                validators.DrawNationCountValidator.message
                % self.variant.max_nations_in_draw
            ),
        )

    def test_duplicate_nations(self):
        data = {'nations': [self.france.id, self.france.id]}
        self.create_test_nation_state(turn=self.turn, nation=self.england)
        self.create_test_nation_state(turn=self.turn, nation=self.france)

        response = self.client.post(self.url, data, format='json')
        error = response.data['non_field_errors'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(error),
            validators.DistinctNationsValidator.message,
        )

    @patch('service.validators.get_combined_strength')
    def test_propose_draw(self, mock_get_combined_strength):
        nations = [self.france, self.germany, self.italy]
        data = {'nations': [n.id for n in nations]}
        mock_get_combined_strength.return_value = 20
        self.create_test_nation_state(turn=self.turn, nation=self.england)
        self.create_test_nation_state(turn=self.turn, nation=self.france)
        self.create_test_nation_state(turn=self.turn, nation=self.germany)
        self.create_test_nation_state(turn=self.turn, nation=self.italy)

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        draw = models.Draw.objects.get()
        draw_nations = list(draw.nations.all())
        for nation in nations:
            self.assertTrue(nation in draw_nations)
        self.assertEqual(draw.proposed_by, self.england)
        self.assertEqual(draw.proposed_by_user, self.user)
        self.assertEqual(draw.turn, self.turn)
        self.assertTrue(draw.proposed_at)


class TestCancelDraw(APITestCase, DiplomacyTestCaseMixin):

    view_name = 'cancel-draw'

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(
            variant=self.variant,
            status=GameStatus.ACTIVE,
        )
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()
        self.other_user = self.create_test_user()
        self.england = self.create_test_nation(
            variant=self.variant,
            name='England',
        )
        self.france = self.create_test_nation(
            variant=self.variant,
            name='France',
        )
        self.game.participants.add(self.user)
        self.england_nation_state = self.create_test_nation_state(
            nation=self.england,
            turn=self.turn,
            user=self.user,
        )
        self.france_nation_state = self.create_test_nation_state(
            nation=self.france,
            turn=self.turn,
            user=self.other_user,
        )
        self.data = {}
        self.client.force_authenticate(user=self.user)

    def test_cannot_cancel_another_players_draw(self):
        draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.france,
            proposed_by_user=self.other_user,
        )
        url = reverse(self.view_name, args=[self.turn.id, draw.id])
        response = self.client.patch(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_cancel_accepted_draw(self):
        draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.england,
            proposed_by_user=self.user,
            status=DrawStatus.ACCEPTED,
        )
        url = reverse(self.view_name, args=[self.turn.id, draw.id])
        response = self.client.patch(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_cancel_rejected_draw(self):
        draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.england,
            proposed_by_user=self.user,
            status=DrawStatus.REJECTED,
        )
        url = reverse(self.view_name, args=[self.turn.id, draw.id])
        response = self.client.patch(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_draw(self):
        draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.england,
            proposed_by_user=self.user,
        )
        url = reverse(self.view_name, args=[self.turn.id, draw.id])
        response = self.client.patch(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        draw.refresh_from_db()
        self.assertEqual(draw.status, DrawStatus.CANCELED)


class TestDrawResponse(APITestCase, DiplomacyTestCaseMixin):

    view_name = 'draw-response'

    def setUp(self):
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(
            variant=self.variant,
            status=GameStatus.ACTIVE,
        )
        self.england = self.create_test_nation(
            variant=self.variant,
            name='England'
        )
        self.france = self.create_test_nation(
            variant=self.variant,
            name='France',
        )
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()
        self.other_user = self.create_test_user()
        self.england_nation_state = self.create_test_nation_state(
            turn=self.turn,
            nation=self.england,
            user=self.user,
        )
        self.game.participants.add(self.user)
        self.draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.france,
            proposed_by_user=self.other_user,
        )
        self.data = {'response': DrawResponse.ACCEPTED}
        self.url = reverse(self.view_name, args=[self.draw.id])
        self.client.force_authenticate(user=self.user)

    def test_cannot_accept_draw_if_surrendering(self):
        self.surrender = models.Surrender.objects.create(
            user=self.user,
            nation_state=self.england_nation_state,
            status=SurrenderStatus.PENDING,
        )
        response = self.client.post(self.url, self.data, format='json')
        error = response.data['non_field_errors'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(error),
            validators.NotSurrenderingValidator.message
        )

    def test_invalid_response_type(self):
        self.data['response'] = 'invalid'
        response = self.client.post(self.url, self.data, format='json')
        error = response.data['response'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(error),
            '"invalid" is not a valid choice.'
        )

    def test_accept_draw_already_accepting(self):
        models.DrawResponse.objects.create(
            draw=self.draw,
            nation=self.england,
            user=self.user,
            response=DrawResponse.ACCEPTED,
        )
        response = self.client.post(self.url, self.data, format='json')
        error = response.data['draw'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(error),
            validators.DrawProposedValidator.message,
        )

    def test_accept_draw_already_rejecting(self):
        models.DrawResponse.objects.create(
            draw=self.draw,
            nation=self.england,
            user=self.user,
            response=DrawResponse.REJECTED,
        )
        response = self.client.post(self.url, self.data, format='json')
        error = response.data['draw'][0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(error),
            validators.DrawProposedValidator.message,
        )

    def test_cannot_accept_canceled_draw(self):
        self.draw.status = DrawStatus.CANCELED
        self.draw.save()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_accept_rejected_draw(self):
        self.draw.status = DrawStatus.REJECTED
        self.draw.save()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_accept_accepted_draw(self):
        self.draw.status = DrawStatus.ACCEPTED
        self.draw.save()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_draw(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        draw_response = models.DrawResponse.objects.get()
        self.assertEqual(draw_response.draw, self.draw)
        self.assertEqual(draw_response.nation, self.england)
        self.assertEqual(draw_response.user, self.user)
        self.assertEqual(draw_response.response, DrawResponse.ACCEPTED)
        self.assertTrue(draw_response.created_at)

    def test_reject_draw(self):
        self.data['response'] = DrawResponse.REJECTED
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        draw_response = models.DrawResponse.objects.get()
        self.assertEqual(draw_response.draw, self.draw)
        self.assertEqual(draw_response.nation, self.england)
        self.assertEqual(draw_response.user, self.user)
        self.assertEqual(draw_response.response, DrawResponse.REJECTED)
        self.assertTrue(draw_response.created_at)


class TestCancelDrawResponse(APITestCase, DiplomacyTestCaseMixin):

    view_name = 'cancel-draw-response'

    def setUp(self):
        self.patch_set_status()
        self.patch_set_winners()
        self.variant = self.create_test_variant()
        self.game = self.create_test_game(
            variant=self.variant,
            status=GameStatus.ACTIVE,
        )
        self.england = self.create_test_nation(
            variant=self.variant,
            name='England'
        )
        self.france = self.create_test_nation(
            variant=self.variant,
            name='France',
        )
        self.turn = self.create_test_turn(game=self.game)
        self.user = self.create_test_user()
        self.other_user = self.create_test_user()
        self.england_nation_state = self.create_test_nation_state(
            turn=self.turn,
            nation=self.england,
            user=self.user,
        )
        self.game.participants.add(self.user)
        self.draw = self.create_test_draw(
            turn=self.turn,
            proposed_by=self.france,
            proposed_by_user=self.other_user,
        )
        self.draw_response = models.DrawResponse.objects.create(
            draw=self.draw,
            user=self.user,
            nation=self.england,
            response=DrawResponse.ACCEPTED,
        )
        self.data = {'response': DrawResponse.ACCEPTED}
        self.client.force_authenticate(user=self.user)

    def test_draw_does_not_exist(self):
        self.url = reverse(
            self.view_name,
            args=[self.draw.id, self.draw_response.id + 1]
        )
        response = self.client.delete(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_players_response(self):
        self.draw_response.nation = self.france
        self.draw_response.user = self.other_user
        self.draw_response.save()
        self.url = reverse(
            self.view_name,
            args=[self.draw.id, self.draw_response.id]
        )
        response = self.client.delete(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_after_draw_accepted(self):
        self.draw.status = DrawStatus.ACCEPTED
        self.draw.save()
        self.url = reverse(
            self.view_name,
            args=[self.draw.id, self.draw_response.id]
        )
        response = self.client.delete(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_response(self):
        self.url = reverse(
            self.view_name,
            args=[self.draw.id, self.draw_response.id]
        )
        response = self.client.delete(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.DrawResponse.objects.count(), 0)
